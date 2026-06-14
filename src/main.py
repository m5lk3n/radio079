from fetch_swr3_data import fetch_swr3_stories, fetch_swr3_articles
from select_swr3_articles import select_swr3_articles
from generate_swr3_podcast_text import generate_swr3_podcast_text


def main():
    fetch_swr3_stories()
    fetch_swr3_articles()
    select_swr3_articles()
    generate_swr3_podcast_text()


if __name__ == "__main__":
    main()
