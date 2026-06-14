#!/usr/bin/env python3

import json
from urllib.parse import urlparse

import feedparser

FEED_URL = "https://www.swr3.de/~rss/index.xml"


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


def fetch_swr3():
    feed = feedparser.parse(FEED_URL)

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

    with open("/app/data/stories.json", "w", encoding="utf-8") as f:
        json.dump(
            stories,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nWrote data/stories-swr3.json")
