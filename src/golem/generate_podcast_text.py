#!/usr/bin/env python3

import json
import os

from openai import OpenAI

from config import OPEN_API_MODEL, GOLEM_PODCAST_ARTICLES_JSON, GOLEM_PODCAST_SCRIPT_TXT

PODCAST_PROMPT = """
Create a 5-minute German IT news podcast.

Requirements:
- German language
- Use informal language
- Around 700 words
- Radio style
- Intro with a greeting that's not time-specific, i.e., use "Hallo" instead of "Guten Morgen". Make it clear, it's a Golem podcast.
- 3 main stories
- Add the following tag between the stories, exactly as written here: <break time="1s"/>
- End with a simple outro, but no call for action, e.g., "Das war's für heute. Vielen Dank fürs Zuhören. Bis zum nächsten Mal."
- Mention source publication names naturally
- No bullet points

Articles:

{context}
"""


def generate_golem_podcast_text():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )

    with open(GOLEM_PODCAST_ARTICLES_JSON, "r", encoding="utf-8") as f:
        articles = json.load(f)

    context = ""
    for article in articles[:4]:
        context += f"""
TITLE: {article['title']}

{article['text'][:4000]}
"""

    response = client.responses.create(
        model=OPEN_API_MODEL,
        input=PODCAST_PROMPT.format(context=context),
    )

    script = response.output_text

    with open(GOLEM_PODCAST_SCRIPT_TXT, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"Wrote {GOLEM_PODCAST_SCRIPT_TXT} ({len(script)} chars)")
