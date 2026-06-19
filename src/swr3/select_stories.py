#!/usr/bin/env python3

import json
import os

from openai import OpenAI

from config import SWR3_STORIES_JSON, SWR3_PODCAST_STORIES_JSON, OPEN_API_MODEL

SELECTION_PROMPT = """
You are an editor for a German radio news podcast.

From the list of stories below, select the 3 most important ones.

Rules:
- No duplicates (same story reported differently counts as one)
- No politics
- No war
- Prioritize world events in this order:
  1. Germany
  2. Europe
  3. World

Return ONLY a JSON array of the selected story indices (0-based), e.g. [2, 5, 11, 14].
No explanation, no markdown, just the JSON array.

Stories:
{stories}
"""


def select_swr3_stories():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )

    with open(SWR3_STORIES_JSON, "r", encoding="utf-8") as f:
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

    with open(SWR3_PODCAST_STORIES_JSON, "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    print("Selected stories:")
    for i, a in zip(indices, selected):
        print(f"  [{i}] {a['title']}")

    print(f"\nWrote {SWR3_PODCAST_STORIES_JSON}")
