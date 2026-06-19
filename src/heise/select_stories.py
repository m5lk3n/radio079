#!/usr/bin/env python3

import json
import os

from openai import OpenAI

from config import HEISE_STORIES_JSON, HEISE_PODCAST_STORIES_JSON, OPEN_API_MODEL

SELECTION_PROMPT = """
You are an editor for a German radio IT news podcast.

From the list of stories below, select the 3 most important ones.

Rules:
- No duplicates (same story reported differently counts as one)
- No politics
- No war
- No Microsoft
- No social media
- No network
- No security, unless it's a major story, related to Android or iOS 
- Prioritize stories in this order:
  1. Cloud
  2. AI
  3. Linux / Open Source

Return ONLY a JSON array of the selected story indices (0-based), e.g. [2, 5, 11, 14].
No explanation, no markdown, just the JSON array.

Stories:
{stories}
"""


def select_heise_stories():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )

    with open(HEISE_STORIES_JSON, "r", encoding="utf-8") as f:
        stories = json.load(f)

    story_list = "\n".join(
        f"[{i}] {a['title']}" for i, a in enumerate(stories)
    )

    response = client.chat.completions.create(
        model=OPEN_API_MODEL,
        messages=[
            {
                "role": "user",
                "content": SELECTION_PROMPT.format(stories=story_list),
            }
        ],
    )

    indices = json.loads(response.choices[0].message.content)
    selected = [stories[i] for i in indices]

    with open(HEISE_PODCAST_STORIES_JSON, "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    print("Selected stories:")
    for i, a in zip(indices, selected):
        print(f"  [{i}] {a['title']}")

    print(f"\nWrote {HEISE_PODCAST_STORIES_JSON}")
