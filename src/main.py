from heise.fetch_podcast import fetch_heise_podcast
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text


def main():
    # fetch_weather_data()
    # generate_weather_text()
    # generate_today_greeting_weather_audio()

    fetch_heise_podcast()

if __name__ == "__main__":
    main()
