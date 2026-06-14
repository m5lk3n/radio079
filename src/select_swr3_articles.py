#!/usr/bin/env python3

import json
import os

from openai import OpenAI

from config import SWR3_ARTICLES_JSON, SWR3_PODCAST_ARTICLES_JSON, OPEN_API_MODEL

SELECTION_PROMPT = """
You are an editor for a German radio news podcast.

From the list of articles below, select the 4 most important ones.

Rules:
- No duplicates (same story reported differently counts as one)
- No politics
- No war
- Prioritize world events in this order:
  1. Germany
  2. Europe
  3. World

Return ONLY a JSON array of the selected article indices (0-based), e.g. [2, 5, 11, 14].
No explanation, no markdown, just the JSON array.

Articles:
{articles}
"""


def select_swr3_articles():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )

    with open(SWR3_ARTICLES_JSON, "r", encoding="utf-8") as f:
        articles = json.load(f)

    article_list = "\n".join(
        f"[{i}] {a['title']}" for i, a in enumerate(articles)
    )

    response = client.chat.completions.create(
        model=OPEN_API_MODEL,
        messages=[
            {
                "role": "user",
                "content": SELECTION_PROMPT.format(articles=article_list),
            }
        ],
    )

    indices = json.loads(response.choices[0].message.content)
    selected = [articles[i] for i in indices]

    with open(SWR3_PODCAST_ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    print("Selected articles:")
    for i, a in zip(indices, selected):
        print(f"  [{i}] {a['title']}")

    print("\nWrote data/selected-articles-swr3.json")
