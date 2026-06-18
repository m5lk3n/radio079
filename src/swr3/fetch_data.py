#!/usr/bin/env python3

import json
from time import sleep
from urllib.parse import urlparse

import feedparser
import trafilatura

from config import SWR3_STORIES_JSON, SWR3_ARTICLES_JSON, SWR3_FEED_URL


def is_valid_url(url: str) -> bool:
    if not url:
        return False

    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )
    except Exception:
        return False


def fetch_swr3_stories():
    feed = feedparser.parse(SWR3_FEED_URL)

    print(f"Feed: {feed.feed.get('title', 'Unknown')}")
    print(f"Entries in feed: {len(feed.entries)}")
    print()

    stories = []
    skipped = 0

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()
        published = entry.get("published", "").strip()
        summary = entry.get("summary", "").strip()

        if not is_valid_url(url):
            skipped += 1
            print(f"Skipping invalid URL (title={title!r}, url={url!r})")
            continue

        if "SWR3" in title:
            skipped += 1
            print(f"Skipping SWR3 title (title={title!r})")
            continue

        stories.append(
            {
                "title": title,
                "url": url,
                "published": published,
                "summary": summary,
            }
        )

    print()
    print(f"Valid stories: {len(stories)}")
    print(f"Skipped: {skipped}")

    with open(SWR3_STORIES_JSON, "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {SWR3_STORIES_JSON}")


def fetch_swr3_articles():
    with open(SWR3_STORIES_JSON, "r", encoding="utf-8") as f:
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

    with open(SWR3_ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {SWR3_ARTICLES_JSON}")
