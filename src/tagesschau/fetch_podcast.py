#!/usr/bin/env python3

import json
import os
import subprocess

import feedparser
import requests

from config import (
    TAGESSCHAU_PODCAST_FEED_URL,
    TAGESSCHAU_PODCAST_MP3,
    TAGESSCHAU_PODCAST_WAV,
    TAGESSCHAU_LAST_EPISODE_JSON,
)


def fetch_tagesschau_podcast():
    feed = feedparser.parse(TAGESSCHAU_PODCAST_FEED_URL)

    if not feed.entries:
        print("No entries in tagesschau podcast feed")
        return

    latest = feed.entries[0]
    guid = latest.get("id", "")

    enclosure_url = None
    for enc in latest.get("enclosures", []):
        if enc.get("type", "").startswith("audio/"):
            enclosure_url = enc.get("href") or enc.get("url")
            break

    if not enclosure_url:
        print("No audio enclosure found in latest tagesschau episode")
        return

    try:
        with open(TAGESSCHAU_LAST_EPISODE_JSON, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    if state.get("guid") == guid and os.path.exists(TAGESSCHAU_PODCAST_WAV):
        print(f"Tagesschau podcast already up to date: {latest.get('title', '')!r}")
        return

    print(f"Downloading tagesschau podcast: {latest.get('title', '')!r}")
    print(f"URL: {enclosure_url}")

    response = requests.get(enclosure_url, stream=True)
    response.raise_for_status()
    with open(TAGESSCHAU_PODCAST_MP3, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            f.write(chunk)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", TAGESSCHAU_PODCAST_MP3,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            TAGESSCHAU_PODCAST_WAV,
        ],
        check=True,
    )
    print(f"Wrote {TAGESSCHAU_PODCAST_WAV}")

    with open(TAGESSCHAU_LAST_EPISODE_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {"guid": guid, "title": latest.get("title", ""), "url": enclosure_url},
            f,
            ensure_ascii=False,
            indent=2,
        )
