#!/usr/bin/env python3

import json
import os
from datetime import date as _date

from openai import OpenAI

from config import (
    OPEN_API_MODEL,
    WEATHER_JSON,
    WEATHER_TEXT_TXT,
)

# WMO weather interpretation codes as used by Open-Meteo
_WEATHER_CODES = {
    0: "klarer Himmel",
    1: "überwiegend klar",
    2: "teilweise bewölkt",
    3: "bedeckt",
    45: "neblig",
    48: "gefrierender Nebel",
    51: "leichter Nieselregen",
    53: "mäßiger Nieselregen",
    55: "starker Nieselregen",
    61: "leichter Regen",
    63: "mäßiger Regen",
    65: "starker Regen",
    71: "leichter Schneefall",
    73: "mäßiger Schneefall",
    75: "starker Schneefall",
    77: "Schneegriesel",
    80: "leichte Regenschauer",
    81: "mäßige Regenschauer",
    82: "starke Regenschauer",
    85: "leichte Schneeschauer",
    86: "starke Schneeschauer",
    95: "Gewitter",
    96: "Gewitter mit leichtem Hagel",
    99: "Gewitter mit starkem Hagel",
}

_GREETING_PROMPT = """
Du bist ein deutschsprachiger Moderator bei Radio 079, einem lokalen Radiosender für {location}.
Schreibe ein kurzes, lebendiges "Hallo" (ca. 60-80 Wörter, jedoch keinen "Guten Morgen"), der das heutige Wetter einbezieht.

Wetterdaten für heute ({date}):
- Aktuell: {current_temp}°C (gefühlt {apparent_temp}°C), {weather_desc}
- Tagesmaximum: {temp_max}°C, Tagesminimum: {temp_min}°C
- Niederschlagswahrscheinlichkeit: {precip_prob}%
- Windgeschwindigkeit: {wind_speed} km/h

Tonvorgabe: Passe deine Stimmung dem Wetter an — bei schönem Wetter lebhaft und fröhlich, bei Regen oder schlechtem Wetter eher nachdenklich oder gemütlich.
Kein Intro — fang direkt mit einer stimmungsvollen Aussage an.
Keine Aufzählungen, fließender Text.
Kein Wechsel der Sprache, bleibe durchgehend auf Deutsch.
"""


def generate_weather_text():
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )

    with open(WEATHER_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    current = data["current"]
    daily = data["daily"]

    weather_code = current["weather_code"]
    weather_desc = _WEATHER_CODES.get(weather_code, f"Wetter (Code {weather_code})")

    _DE_DAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    today = _date.today()
    date_str = f"{_DE_DAYS[today.weekday()]}, {today.strftime('%d.%m.%Y')}"

    prompt = _GREETING_PROMPT.format(
        date=date_str,
        location=os.environ["WEATHER_LOCATION_NAME"],
        current_temp=current["temperature_2m"],
        apparent_temp=current["apparent_temperature"],
        weather_desc=weather_desc,
        temp_max=daily["temperature_2m_max"][0],
        temp_min=daily["temperature_2m_min"][0],
        precip_prob=daily["precipitation_probability_max"][0],
        wind_speed=current["wind_speed_10m"],
    )

    response = client.responses.create(
        model=OPEN_API_MODEL,
        input=prompt,
    )

    text = response.output_text

    with open(WEATHER_TEXT_TXT, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Wrote {WEATHER_TEXT_TXT} ({len(text)} chars)")
