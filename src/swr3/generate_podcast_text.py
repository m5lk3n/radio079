#!/usr/bin/env python3

import json
import os

from openai import OpenAI

from config import OPEN_API_MODEL, SWR3_PODCAST_ARTICLES_JSON, SWR3_PODCAST_SCRIPT_TXT

PODCAST_PROMPT = """
Create a 5-minute German news podcast.

Requirements:
- German language
- Use informal language
- Around 700 words
- Radio style
- Intro with a greeting that's not time-specific, i.e., use "Hallo" instead of "Guten Morgen". Make it clear, it's an SWR3 podcast.
- 4 main stories
- Pause between stories
- Outro
- Mention source publication names naturally
- No bullet points

Articles:

{context}
"""


def generate_swr3_podcast_text():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )

    with open(SWR3_PODCAST_ARTICLES_JSON, "r", encoding="utf-8") as f:
        articles = json.load(f)

    context = ""
    for article in articles[:5]:
        context += f"""
TITLE: {article['title']}

{article['text'][:4000]}
"""

    response = client.responses.create(
        model=OPEN_API_MODEL,
        input=PODCAST_PROMPT.format(context=context),
    )

    script = response.output_text

    with open(SWR3_PODCAST_SCRIPT_TXT, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"Wrote {SWR3_PODCAST_SCRIPT_TXT} ({len(script)} chars)")
