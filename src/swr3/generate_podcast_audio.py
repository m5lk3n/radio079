#!/usr/bin/env python3

import subprocess

import cartesia
from config import (
    SWR3_PODCAST_SCRIPT_TXT,
    SWR3_PODCAST_WAV_RAW,
    SWR3_PODCAST_WAV,
)


def generate_swr3_podcast_audio():
    with open(SWR3_PODCAST_SCRIPT_TXT, "r", encoding="utf-8") as f:
        script = f.read()

    cartesia.tts(script, cartesia.FEMALE_VOICE_ID, "excited", SWR3_PODCAST_WAV_RAW)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", SWR3_PODCAST_WAV_RAW,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            SWR3_PODCAST_WAV,
        ],
        check=True,
    )
    print(f"Wrote {SWR3_PODCAST_WAV}")
