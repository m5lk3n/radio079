#!/usr/bin/env python3

import subprocess

from config import (
    HEISE_PODCAST_SCRIPT_TXT,
    HEISE_PODCAST_WAV_RAW,
    HEISE_PODCAST_WAV,
    TTS_MODEL,
)

# Does the following on the command line:
#  cat podcast_script_heise.txt | piper -m de_DE-thorsten-high.onnx -f podcast.wav
#  ffmpeg -i podcast.wav -af loudnorm=I=-16:LRA=11:TP=-1.5 podcast_heise.wav
def generate_heise_podcast_audio():
    with open(HEISE_PODCAST_SCRIPT_TXT, "r", encoding="utf-8") as f:
        script = f.read()

    subprocess.run(
        ["piper", "-m", TTS_MODEL, "-f", HEISE_PODCAST_WAV_RAW],
        input=script.encode(),
        check=True,
    )
    print(f"Wrote {HEISE_PODCAST_WAV_RAW}")

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
