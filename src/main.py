from swr3.fetch_data import fetch_swr3_stories, fetch_swr3_articles
from swr3.generate_podcast_audio import generate_swr3_podcast_audio
from swr3.generate_podcast_text import generate_swr3_podcast_text
from swr3.select_articles import select_swr3_articles
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text


def main():
    fetch_weather_data()
    generate_weather_text()
    generate_today_greeting_weather_audio()

    fetch_swr3_stories()
    fetch_swr3_articles()
    select_swr3_articles()
    generate_swr3_podcast_text()
    generate_swr3_podcast_audio()


if __name__ == "__main__":
    main()
