#!/usr/bin/env python3

import json
import os
import subprocess
import time
import urllib.error

import feedparser
import requests

from config import (
    TAGESSCHAU_PODCAST_FEED_URL,
    TAGESSCHAU_LAST_EPISODE_JSON,
)


def fetch_tagesschau_podcast(mp3_path: str, wav_path: str):
    last_exc = None
    for attempt in range(3):
        feed = feedparser.parse(TAGESSCHAU_PODCAST_FEED_URL)
        bozo_exc = feed.get("bozo_exception")
        if feed.entries or not (bozo_exc and isinstance(bozo_exc, (urllib.error.URLError, OSError))):
            break
        last_exc = bozo_exc
        if attempt < 2:
            print(f"Feed fetch failed (attempt {attempt + 1}/3): {bozo_exc}, retrying...")
            time.sleep(5)
    else:
        print(f"Failed to fetch tagesschau feed after 3 attempts: {last_exc}")
        return

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

    if state.get("guid") == guid and os.path.exists(wav_path):
        print(f"Tagesschau podcast already up to date: {latest.get('title', '')!r}")
        return

    print(f"Downloading tagesschau podcast: {latest.get('title', '')!r}")
    print(f"URL: {enclosure_url}")

    last_exc = None
    for attempt in range(3):
        try:
            response = requests.get(enclosure_url, stream=True)
            response.raise_for_status()
            with open(mp3_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):
                    f.write(chunk)
            break
        except requests.RequestException as e:
            last_exc = e
            if attempt < 2:
                print(f"Download failed (attempt {attempt + 1}/3): {e}, retrying...")
                time.sleep(5)
    else:
        print(f"Failed to download tagesschau podcast after 3 attempts: {last_exc}")
        return

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", mp3_path,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            "-ar", "44100",
            wav_path,
        ],
        check=True,
    )
    print(f"Wrote {wav_path}")

    with open(TAGESSCHAU_LAST_EPISODE_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {"guid": guid, "title": latest.get("title", ""), "url": enclosure_url},
            f,
            ensure_ascii=False,
            indent=2,
        )
