import os

from fetch_swr3_stories import fetch_swr3_stories
from fetch_swr3_articles import fetch_swr3_articles


def main():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    print(openai_api_key[:4])
    fetch_swr3_stories()
    fetch_swr3_articles()


if __name__ == "__main__":
    main()
