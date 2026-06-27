import os
from typing import Any

import requests

_API_URL = "https://api.cartesia.ai/tts/bytes"
_API_VERSION = "2026-03-01"
_MODEL_ID = "sonic-3.5"

FEMALE_VOICE_ID = "38aabb6a-f52b-4fb0-a3d1-988518f4dc06"
MALE_VOICE_ID = "b7187e84-fe22-4344-ba4a-bc013fcb533e"

_BAD_WEATHER_CODES = {
    45, 48,               # fog
    51, 53, 55, 56, 57,   # drizzle / freezing drizzle
    61, 63, 65, 66, 67,   # rain / freezing rain
    80, 81, 82,           # rain showers
    95, 96, 99,           # thunderstorm
}


def weather_emotion(weather_code: int) -> str:
    return "sad" if weather_code in _BAD_WEATHER_CODES else "excited"


def tts(text: str, voice_id: str, emotion: str, output_path: str) -> None:
    payload: dict[str, Any] = {
        "model_id": _MODEL_ID,
        "transcript": text,
        "voice": {
            "mode": "id",
            "id": voice_id,
        },
        "output_format": {
            "container": "wav",
            "encoding": "pcm_s16le",
            "sample_rate": 44100,
        },
        "language": "de",
        "generation_config": {
            "speed": 1,
            "volume": 1,
            "emotion": emotion,
        },
    }

    response = requests.post(
        _API_URL,
        headers={
            "Cartesia-Version": _API_VERSION,
            "X-API-Key": os.environ["CARTESIA_API_KEY"],
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Wrote {output_path}")
