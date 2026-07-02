#!/usr/bin/env python3

import json
import random
import subprocess

import cartesia


def generate_today_greeting_weather_audio(
    weather_json: str,
    weather_text_txt: str,
    weather_wav: str,
    weather_wav_raw: str,
):
    with open(weather_text_txt, "r", encoding="utf-8") as f:
        text = f.read()

    with open(weather_json, "r", encoding="utf-8") as f:
        weather = json.load(f)
    weather_code = weather["current"]["weather_code"]
    emotion = cartesia.weather_emotion(weather_code)

    voice_id = random.choice([cartesia.FEMALE_VOICE_ID, cartesia.MALE_VOICE_ID])
    cartesia.tts(text, voice_id, emotion, weather_wav_raw)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", weather_wav_raw,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            "-ar", "44100",
            weather_wav,
        ],
        check=True,
    )
    print(f"Wrote {weather_wav}")
