import os
import stable_whisper
from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, Form
from fastapi.openapi.utils import get_openapi
import json

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
    text: str
    segments: list[WhisperSegment]
    language: str

def toStandardWhisperResult(result: stable_whisper.result.WhisperResult) -> WhisperResult:
    return WhisperResult(
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
        language=result.language
    )

app = FastAPI()

@app.post("/api/align", response_model=WhisperResult)
async def align_text_with_audio(audio: UploadFile, text: UploadFile, language: Annotated[str, Form(examples=["en"])]):
    audioRaw = await audio.read()
    textRaw = await text.read()
    textUtf8 = textRaw.decode("utf-8")

    model_name = os.environ.get("MODEL", "base")
    model = stable_whisper.load_model(model_name)

    alignment: stable_whisper.result.WhisperResult = model.align(audioRaw, textUtf8, language=language, fast_mode=True)
    return toStandardWhisperResult(alignment)



with open('openapi.json', 'w') as f:
    json.dump(get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes
    ), f)