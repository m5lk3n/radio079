#!/usr/bin/env python3

import random
import subprocess

import cartesia
from config import (
    HEISE_PODCAST_SCRIPT_TXT,
    HEISE_PODCAST_WAV_RAW,
    HEISE_PODCAST_WAV,
)

_MALE_EMOTIONS = ["calm", "excited", "neutral"]


def generate_heise_podcast_audio():
    with open(HEISE_PODCAST_SCRIPT_TXT, "r", encoding="utf-8") as f:
        script = f.read()

    emotion = random.choice(_MALE_EMOTIONS)
    cartesia.tts(script, cartesia.MALE_VOICE_ID, emotion, HEISE_PODCAST_WAV_RAW)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", HEISE_PODCAST_WAV_RAW,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            HEISE_PODCAST_WAV,
        ],
        check=True,
    )
    print(f"Wrote {HEISE_PODCAST_WAV}")
