from pathlib import Path

from heise.fetch_podcast import fetch_heise_podcast
from tagesschau.fetch_podcast import fetch_tagesschau_podcast
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text
from config import WEATHER_WAV


def main():
    if Path(WEATHER_WAV).exists():
        print(f"Weather already generated today, skipping ({WEATHER_WAV})")
    else:
        fetch_weather_data()
        generate_weather_text()
        generate_today_greeting_weather_audio()

    fetch_heise_podcast()
    fetch_tagesschau_podcast()
    
if __name__ == "__main__":
    main()
