#!/usr/bin/env python3

import subprocess

from config import (
    SWR3_PODCAST_SCRIPT_TXT,
    SWR3_PODCAST_WAV_RAW,
    SWR3_PODCAST_WAV,
    TTS_MODEL,
)

# Does the following on the command line:
#  cat podcast_script_swr3.txt | piper -m de_DE-thorsten-high.onnx -f podcast.wav
#  ffmpeg -i podcast.wav -af loudnorm=I=-16:LRA=11:TP=-1.5 podcast_swr3.wav
def generate_swr3_podcast_audio():
    with open(SWR3_PODCAST_SCRIPT_TXT, "r", encoding="utf-8") as f:
        script = f.read()

    subprocess.run(
        ["piper", "-m", TTS_MODEL, "-f", SWR3_PODCAST_WAV_RAW],
        input=script.encode(),
        check=True,
    )
    print(f"Wrote {SWR3_PODCAST_WAV_RAW}")

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
