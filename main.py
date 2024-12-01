import os
import stable_whisper
from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, Form
from fastapi.openapi.utils import get_openapi
import json
import whisper

import stable_whisper.alignment
import stable_whisper.audio
import stable_whisper.timing

class WhisperWord(BaseModel):
    word: str
    start: float
    end: float
    probability: float

class WhisperSegment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list
    temperature: float
    avgLogprob: float
    compressionRatio: float
    noSpeechProb: float
    words: list[WhisperWord]

class WhisperResult(BaseModel):
    quality: float
    text: str
    segments: list[WhisperSegment]
    language: str

def wordQuality(word: stable_whisper.result.WordTiming) -> float:
    return 0 if word.start >= word.end else word.probability

def segmentQuality(segment: stable_whisper.result.Segment) -> float:
    return sum(wordQuality(word) for word in segment.words) / len(segment.words)

def resultQuality(result: stable_whisper.result.WhisperResult) -> float:
    return sum(segmentQuality(segment) for segment in result.segments) / len(result.segments)

def toStandardWhisperResult(result: stable_whisper.result.WhisperResult, language: str) -> WhisperResult:
    return WhisperResult(
        quality=resultQuality(result),
        text=result.text,
        segments=[
            WhisperSegment(
                id=i,
                seek=0,
                start=segment.start,
                end=segment.end,
                text=segment.text,
                tokens=[],
                temperature=0,
                avgLogprob=0,
                compressionRatio=0,
                noSpeechProb=0,
                words=[
                    WhisperWord(
                        word=word.word,
                        start=word.start,
                        end=word.end,
                        probability=word.probability
                    )
                    for word in segment.words
                ]
            )
            for i, segment in enumerate(result.segments)
        ],
        language=language
    )

class LocateResult(BaseModel):
    start: float
    end: float

def toStandardLocateResult(result: stable_whisper.result.Segment) -> LocateResult:
    return LocateResult(
        start=result.start,
        end=result.end
    )

app = FastAPI()

print("Available models:")
for model_name in whisper.available_models():
    print(f"  {model_name}")

model_name = os.environ.get("MODEL", "large-v3-turbo")
model = stable_whisper.load_model(model_name)

@app.post("/api/align", response_model=WhisperResult)
async def align_text_with_audio(audio: UploadFile, text: UploadFile, language: Annotated[str, Form(examples=["en"])], fast_mode: Annotated[bool, Form()] = False):
    audioRaw = await audio.read()
    textRaw = await text.read()
    textUtf8 = textRaw.decode("utf-8")

    alignment = stable_whisper.alignment.align(model, audioRaw, textUtf8, language=language, fast_mode=fast_mode)
    print(f"Align Quality: {resultQuality(alignment)}")

    stable_whisper.alignment.refine(model, audioRaw, alignment, inplace=True)
    print(f"Refine Quality: {resultQuality(alignment)}")

    alignment.adjust_by_silence()
    print(f"Adjust Quality: {resultQuality(alignment)}")

    return toStandardWhisperResult(alignment, language)

@app.post("/api/transcribe", response_model=WhisperResult)
async def transcribe_audio(audio: UploadFile, language: Annotated[str, Form(examples=["en"])]):
    audioRaw = await audio.read()
    
    transcription = model.transcribe(audioRaw, language=language)
    return toStandardWhisperResult(transcription, language)

with open('openapi.json', 'w') as f:
    json.dump(get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes
    ), f)