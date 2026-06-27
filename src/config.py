import shutil
from datetime import date, timedelta
from pathlib import Path

_DATA_ROOT = Path("/app/data")
_DATE_DIR = _DATA_ROOT / date.today().strftime("%Y%m%d")
_HEISE_DIR = _DATE_DIR / "heise"
_TAGESSCHAU_DIR = _DATE_DIR / "tagesschau"
_WEATHER_DIR = _DATE_DIR / "weather"
_HEISE_DIR.mkdir(parents=True, exist_ok=True)
_TAGESSCHAU_DIR.mkdir(parents=True, exist_ok=True)
_WEATHER_DIR.mkdir(parents=True, exist_ok=True)

# The following maintenance runs at import time — when config.py is first imported,
# it iterates /app/data, parses each subdirectory name as a YYYYMMDD date,
# and removes (via shutil.rmtree) any that are older than 7 days.
# Non-matching directory names are silently skipped.
_CUTOFF = date.today() - timedelta(days=7)
for _d in _DATA_ROOT.iterdir():
    if _d.is_dir():
        try:
            if date.fromisoformat(_d.name[:4] + "-" + _d.name[4:6] + "-" + _d.name[6:8]) < _CUTOFF:
                shutil.rmtree(_d)
        except ValueError:
            pass

WEATHER_JSON = str(_WEATHER_DIR / "weather.json")
WEATHER_TEXT_TXT = str(_WEATHER_DIR / "weather_text.txt")
WEATHER_WAV_RAW = str(_WEATHER_DIR / "weather_raw.wav")
WEATHER_WAV = str(_WEATHER_DIR / "weather.wav")

HEISE_PODCAST_FEED_URL = "https://kurzinformiert.podigee.io/feed/mp3"
HEISE_LAST_EPISODE_JSON = str(_DATA_ROOT / "heise_last_episode.json")
HEISE_PODCAST_MP3 = str(_HEISE_DIR / "podcast_raw.mp3")
HEISE_PODCAST_WAV = str(_HEISE_DIR / "podcast.wav")

TAGESSCHAU_PODCAST_FEED_URL = "https://www.tagesschau.de/multimedia/sendung/tagesschau_in_100_sekunden/podcast-ts100-audio-100~podcast.xml"
TAGESSCHAU_LAST_EPISODE_JSON = str(_DATA_ROOT / "tagesschau_last_episode.json")
TAGESSCHAU_PODCAST_MP3 = str(_TAGESSCHAU_DIR / "podcast_raw.mp3")
TAGESSCHAU_PODCAST_WAV = str(_TAGESSCHAU_DIR / "podcast.wav")

