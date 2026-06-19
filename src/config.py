import shutil
from datetime import date, timedelta
from pathlib import Path

_DATA_ROOT = Path("/app/data")
_DATE_DIR = _DATA_ROOT / date.today().strftime("%Y%m%d")
_SWR3_DIR = _DATE_DIR / "swr3"
_HEISE_DIR = _DATE_DIR / "heise"
_WEATHER_DIR = _DATE_DIR / "weather"
_SWR3_DIR.mkdir(parents=True, exist_ok=True)
_HEISE_DIR.mkdir(parents=True, exist_ok=True)
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

OPEN_API_MODEL = "gpt-5.4-nano"
TTS_MODEL = "/app/tts/de_DE-thorsten-high.onnx"

SWR3_FEED_URL = "https://www.swr3.de/~rss/index.xml"
SWR3_STORIES_JSON = str(_SWR3_DIR / "stories.json")
SWR3_PODCAST_STORIES_JSON = str(_SWR3_DIR / "podcast-stories.json")
SWR3_PODCAST_ARTICLES_JSON = str(_SWR3_DIR / "podcast-articles.json")
SWR3_PODCAST_SCRIPT_TXT = str(_SWR3_DIR / "podcast_script.txt")
SWR3_PODCAST_WAV_RAW = str(_SWR3_DIR / "podcast_raw.wav")
SWR3_PODCAST_WAV = str(_SWR3_DIR / "podcast.wav")

HEISE_TOP_FEED_URL = "https://www.heise.de/rss/heise-top-atom.xml"
HEISE_IT_FEED_URL = "https://www.heise.de/rss/heise-Rubrik-IT-atom.xml"
HEISE_STORIES_JSON = str(_HEISE_DIR / "stories.json")
HEISE_PODCAST_STORIES_JSON = str(_HEISE_DIR / "podcast-stories.json")
HEISE_PODCAST_ARTICLES_JSON = str(_HEISE_DIR / "podcast-articles.json")
HEISE_PODCAST_SCRIPT_TXT = str(_HEISE_DIR / "podcast_script.txt")
HEISE_PODCAST_WAV_RAW = str(_HEISE_DIR / "podcast_raw.wav")
HEISE_PODCAST_WAV = str(_HEISE_DIR / "podcast.wav")

WEATHER_JSON = str(_WEATHER_DIR / "weather.json")
WEATHER_TEXT_TXT = str(_WEATHER_DIR / "weather_text.txt")
WEATHER_WAV_RAW = str(_WEATHER_DIR / "weather_raw.wav")
WEATHER_WAV = str(_WEATHER_DIR / "weather.wav")
