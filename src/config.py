import os
import shutil
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

_tf = TimezoneFinder()
_tz_name = _tf.timezone_at(
    lat=float(os.environ["WEATHER_LOCATION_LAT"]),
    lng=float(os.environ["WEATHER_LOCATION_LON"]),
)
if _tz_name is None:
    raise RuntimeError(
        "Could not determine timezone for "
        f"WEATHER_LOCATION_LAT={os.environ['WEATHER_LOCATION_LAT']}, "
        f"WEATHER_LOCATION_LON={os.environ['WEATHER_LOCATION_LON']}"
    )
_LOCAL_TZ = ZoneInfo(_tz_name)


def is_weekend() -> bool:
    """True on Saturdays and Sundays in the configured local timezone.

    Used to suspend audio fetching over the weekend.
    """
    return datetime.now(_LOCAL_TZ).weekday() >= 5


_DATA_ROOT = Path("/app/data")

# Feeds and per-source state that don't depend on the date stay module-level.
HEISE_PODCAST_FEED_URL = "https://kurzinformiert.podigee.io/feed/mp3"
HEISE_LAST_EPISODE_JSON = str(_DATA_ROOT / "heise_last_episode.json")

TAGESSCHAU_PODCAST_FEED_URL = "https://www.tagesschau.de/multimedia/sendung/tagesschau_in_100_sekunden/podcast-ts100-audio-100~podcast.xml"
TAGESSCHAU_LAST_EPISODE_JSON = str(_DATA_ROOT / "tagesschau_last_episode.json")


@dataclass(frozen=True)
class DailyPaths:
    """Audio/data file paths for a single day, under data/YYYYMMDD/."""

    weather_json: str
    weather_text_txt: str
    weather_wav_raw: str
    weather_wav: str
    heise_mp3: str
    heise_wav: str
    tagesschau_mp3: str
    tagesschau_wav: str


def _cleanup_old_date_dirs() -> None:
    """Remove data/YYYYMMDD/ folders older than 7 days; skip non-date names."""
    cutoff = datetime.now(_LOCAL_TZ).date() - timedelta(days=7)
    for d in _DATA_ROOT.iterdir():
        if d.is_dir():
            try:
                if date.fromisoformat(d.name[:4] + "-" + d.name[4:6] + "-" + d.name[6:8]) < cutoff:
                    shutil.rmtree(d)
            except ValueError:
                pass


def today_paths() -> DailyPaths:
    """Paths for the current local day, creating the dirs and pruning old ones.

    Recomputed on each call so a long-running process rolls over to a new
    date folder at midnight (and refreshes the once-per-day weather greeting).
    """
    date_dir = _DATA_ROOT / datetime.now(_LOCAL_TZ).strftime("%Y%m%d")
    heise_dir = date_dir / "heise"
    tagesschau_dir = date_dir / "tagesschau"
    weather_dir = date_dir / "weather"
    for d in (heise_dir, tagesschau_dir, weather_dir):
        d.mkdir(parents=True, exist_ok=True)
    _cleanup_old_date_dirs()
    return DailyPaths(
        weather_json=str(weather_dir / "weather.json"),
        weather_text_txt=str(weather_dir / "weather_text.txt"),
        weather_wav_raw=str(weather_dir / "weather_raw.wav"),
        weather_wav=str(weather_dir / "weather.wav"),
        heise_mp3=str(heise_dir / "podcast_raw.mp3"),
        heise_wav=str(heise_dir / "podcast.wav"),
        tagesschau_mp3=str(tagesschau_dir / "podcast_raw.mp3"),
        tagesschau_wav=str(tagesschau_dir / "podcast.wav"),
    )

