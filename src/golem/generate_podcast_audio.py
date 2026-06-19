#!/usr/bin/env python3

import subprocess

from config import (
    GOLEM_PODCAST_SCRIPT_TXT,
    GOLEM_PODCAST_WAV_RAW,
    GOLEM_PODCAST_WAV,
    TTS_MODEL,
)


def generate_golem_podcast_audio():
    with open(GOLEM_PODCAST_SCRIPT_TXT, "r", encoding="utf-8") as f:
        script = f.read()

    subprocess.run(
        ["piper", "-m", TTS_MODEL, "-f", GOLEM_PODCAST_WAV_RAW],
        input=script.encode(),
        check=True,
    )
    print(f"Wrote {GOLEM_PODCAST_WAV_RAW}")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", GOLEM_PODCAST_WAV_RAW,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            GOLEM_PODCAST_WAV,
        ],
        check=True,
    )
    print(f"Wrote {GOLEM_PODCAST_WAV}")
