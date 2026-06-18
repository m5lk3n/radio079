#!/usr/bin/env python3

import json
from time import sleep
from urllib.parse import urlparse

import feedparser
import trafilatura

from config import HEISE_STORIES_JSON, HEISE_ARTICLES_JSON, HEISE_TOP_FEED_URL, HEISE_IT_FEED_URL


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


def fetch_heise_stories():
    feed_urls = [
        # HEISE_TOP_FEED_URL,
        HEISE_IT_FEED_URL,
    ]

    seen_urls = set()
    stories = []
    skipped = 0

    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)
        print(f"Feed: {feed.feed.get('title', 'Unknown')}")
        print(f"Entries in feed: {len(feed.entries)}")
        print()

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()
            published = entry.get("published", "").strip()
            summary = entry.get("summary", "").strip()

            if not is_valid_url(url):
                skipped += 1
                print(f"Skipping invalid URL (title={title!r}, url={url!r})")
                continue

            if "software-architektur.tv" in title:
                skipped += 1
                print(f"Skipping software-architektur.tv title (title={title!r})")
                continue

            if "heise" in title:
                skipped += 1
                print(f"Skipping heise title (title={title!r})")
                continue

            if url in seen_urls:
                skipped += 1
                print(f"Skipping duplicate (title={title!r})")
                continue

            seen_urls.add(url)
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

    with open(HEISE_STORIES_JSON, "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {HEISE_STORIES_JSON}")


def fetch_heise_articles():
    with open(HEISE_STORIES_JSON, "r", encoding="utf-8") as f:
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

    with open(HEISE_ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {HEISE_ARTICLES_JSON}")
