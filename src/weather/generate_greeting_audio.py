#!/usr/bin/env python3

import json
import random
import subprocess

import cartesia
from config import (
    WEATHER_JSON,
    WEATHER_TEXT_TXT,
    WEATHER_WAV,
    WEATHER_WAV_RAW,
)


def generate_today_greeting_weather_audio():
    with open(WEATHER_TEXT_TXT, "r", encoding="utf-8") as f:
        text = f.read()

    with open(WEATHER_JSON, "r", encoding="utf-8") as f:
        weather = json.load(f)
    weather_code = weather["current"]["weather_code"]
    emotion = cartesia.weather_emotion(weather_code)

    voice_id = random.choice([cartesia.FEMALE_VOICE_ID, cartesia.MALE_VOICE_ID])
    cartesia.tts(text, voice_id, emotion, WEATHER_WAV_RAW)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", WEATHER_WAV_RAW,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            WEATHER_WAV,
        ],
        check=True,
    )
    print(f"Wrote {WEATHER_WAV}")
