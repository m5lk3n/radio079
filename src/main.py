import argparse
from pathlib import Path

from heise.fetch_podcast import fetch_heise_podcast
from tagesschau.fetch_podcast import fetch_tagesschau_podcast
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text
from config import WEATHER_WAV


def main() -> None:
    parser = argparse.ArgumentParser(description="radio 0 7 9")
    parser.add_argument("--webserver", action="store_true", help="Start web streaming server on port 8079")
    args = parser.parse_args()

    if args.webserver:
        from webserver import run_webserver
        run_webserver()
        return

    if Path(WEATHER_WAV).exists():
        print("Weather already up to date")
    else:
        fetch_weather_data()
        generate_weather_text()
        generate_today_greeting_weather_audio()

    fetch_heise_podcast()
    fetch_tagesschau_podcast()


if __name__ == "__main__":
    main()
