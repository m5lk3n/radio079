#!/usr/bin/env python3

import json
import trafilatura
from time import sleep

from config import STORIES_SWR3_PATH, ARTICLES_SWR3_PATH


def fetch_swr3_articles():
    with open(STORIES_SWR3_PATH, "r", encoding="utf-8") as f:
        stories = json.load(f)

    results = []

    for story in stories:
        url = story["url"]

        try:
            downloaded = trafilatura.fetch_url(url)

            if downloaded:
                text = trafilatura.extract(downloaded)

                results.append({
                    "title": story["title"],
                    "url": url,
                    "published": story.get("published"),
                    "text": text,
                })

                print(f"✓ {story['title']}")

            sleep(1)

        except Exception as e:
            print(f"✗ {url}: {e}")

    with open(ARTICLES_SWR3_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nWrote data/articles-swr3.json")