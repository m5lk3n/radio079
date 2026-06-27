from heise.fetch_data import fetch_heise_stories, fetch_heise_articles
from heise.select_stories import select_heise_stories
from heise.generate_podcast_audio import generate_heise_podcast_audio
from heise.generate_podcast_text import generate_heise_podcast_text
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text


def main():
    fetch_weather_data()
    generate_weather_text()
    generate_today_greeting_weather_audio()

    fetch_heise_stories()
    select_heise_stories()
    fetch_heise_articles()
    generate_heise_podcast_text()
    generate_heise_podcast_audio()

if __name__ == "__main__":
    main()
