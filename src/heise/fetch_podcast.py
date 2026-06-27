#!/usr/bin/env python3

import json
import os
import subprocess

import feedparser
import requests

from config import (
    HEISE_PODCAST_FEED_URL,
    HEISE_PODCAST_MP3,
    HEISE_PODCAST_WAV,
    HEISE_LAST_EPISODE_JSON,
)


def fetch_heise_podcast():
    feed = feedparser.parse(HEISE_PODCAST_FEED_URL)

    if not feed.entries:
        print("No entries in heise podcast feed")
        return

    latest = feed.entries[0]
    guid = latest.get("id", "")

    enclosure_url = None
    for enc in latest.get("enclosures", []):
        if enc.get("type", "").startswith("audio/"):
            enclosure_url = enc.get("href") or enc.get("url")
            break

    if not enclosure_url:
        print("No audio enclosure found in latest heise episode")
        return

    try:
        with open(HEISE_LAST_EPISODE_JSON, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    if state.get("guid") == guid and os.path.exists(HEISE_PODCAST_WAV):
        print(f"Heise podcast already up to date: {latest.get('title', '')!r}")
        return

    print(f"Downloading heise podcast: {latest.get('title', '')!r}")
    print(f"URL: {enclosure_url}")

    response = requests.get(enclosure_url, stream=True)
    response.raise_for_status()
    with open(HEISE_PODCAST_MP3, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            f.write(chunk)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", HEISE_PODCAST_MP3,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            HEISE_PODCAST_WAV,
        ],
        check=True,
    )
    print(f"Wrote {HEISE_PODCAST_WAV}")

    with open(HEISE_LAST_EPISODE_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {"guid": guid, "title": latest.get("title", ""), "url": enclosure_url},
            f,
            ensure_ascii=False,
            indent=2,
        )
