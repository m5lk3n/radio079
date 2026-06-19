from golem.fetch_data import fetch_golem_stories, fetch_golem_articles
from golem.select_stories import select_golem_stories
from golem.generate_podcast_text import generate_golem_podcast_text
from golem.generate_podcast_audio import generate_golem_podcast_audio
from heise.fetch_data import fetch_heise_stories, fetch_heise_articles
from heise.select_stories import select_heise_stories
from heise.generate_podcast_audio import generate_heise_podcast_audio
from heise.generate_podcast_text import generate_heise_podcast_text
from swr3.fetch_data import fetch_swr3_stories, fetch_swr3_articles
from swr3.generate_podcast_audio import generate_swr3_podcast_audio
from swr3.generate_podcast_text import generate_swr3_podcast_text
from swr3.select_stories import select_swr3_stories
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text


def main():
    fetch_golem_stories()
    select_golem_stories()
    fetch_golem_articles()
    generate_golem_podcast_text()
    generate_golem_podcast_audio()

    fetch_heise_stories()
    select_heise_stories()
    fetch_heise_articles()
    generate_heise_podcast_text()
    generate_heise_podcast_audio()

    fetch_weather_data()
    generate_weather_text()
    generate_today_greeting_weather_audio()

    fetch_swr3_stories()
    select_swr3_stories()
    fetch_swr3_articles()
    generate_swr3_podcast_text()
    generate_swr3_podcast_audio()


if __name__ == "__main__":
    main()
