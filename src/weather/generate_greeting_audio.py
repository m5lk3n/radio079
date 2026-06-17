#!/usr/bin/env python3

import subprocess

from config import (
    SWR3_TTS_MODEL,
    WEATHER_TEXT_TXT,
    WEATHER_WAV,
    WEATHER_WAV_RAW,
)


def generate_today_greeting_weather_audio():
    with open(WEATHER_TEXT_TXT, "r", encoding="utf-8") as f:
        text = f.read()

    subprocess.run(
        ["piper", "-m", SWR3_TTS_MODEL, "-f", WEATHER_WAV_RAW],
        input=text.encode(),
        check=True,
    )
    print(f"Wrote {WEATHER_WAV_RAW}")

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
