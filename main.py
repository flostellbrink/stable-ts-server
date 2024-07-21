import os
import stable_whisper
from typing import Annotated
from fastapi import FastAPI, UploadFile, Form
from fastapi.openapi.utils import get_openapi
import json

app = FastAPI()

class Segment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

def toStandardWhisperResult(result: stable_whisper.result.WhisperResult):
    return {
        "text": result.text,
        "segments": [
            {
                "id": i,
                "seek": 0,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "tokens": [],
                "temperature": 0,
                "avgLogprob": 0,
                "compressionRatio": 0,
                "noSpeechProb": 0,
                "words": [
                    {
                        "word": word.word,
                        "start": word.start,
                        "end": word.end,
                        "probability": word.probability
                    }
                    for word in segment.words
                ]
            }
            for i, segment in enumerate(result.segments)
        ],
        "language": result.language
    }

@app.post("/api/align")
async def align_text_with_audio(audio: UploadFile, text: UploadFile, language: Annotated[str, Form(examples=["en"])], offset: Annotated[int, Form()] = 0):
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