import argparse
from pathlib import Path

from heise.fetch_podcast import fetch_heise_podcast
from tagesschau.fetch_podcast import fetch_tagesschau_podcast
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text
from config import suspend_over_weekend, today_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="radio 0 7 9")
    parser.add_argument("--webserver", action="store_true", help="Start web streaming server on port 8079")
    args = parser.parse_args()

    if args.webserver:
        from webserver import run_webserver
        run_webserver()
        return

    # Suspend over the weekend when enabled: skip all fetching.
    if suspend_over_weekend():
        print("Weekend: suspending audio fetching until Monday")
        return

    paths = today_paths()

    if Path(paths.weather_wav).exists():
        print("Weather already up to date")
    else:
        fetch_weather_data(paths.weather_json)
        generate_weather_text(paths.weather_json, paths.weather_text_txt)
        generate_today_greeting_weather_audio(
            paths.weather_json, paths.weather_text_txt, paths.weather_wav, paths.weather_wav_raw
        )

    fetch_heise_podcast(paths.heise_mp3, paths.heise_wav)
    fetch_tagesschau_podcast(paths.tagesschau_mp3, paths.tagesschau_wav)


if __name__ == "__main__":
    main()
