#!/usr/bin/env python3

import json
import os

import requests

from config import WEATHER_JSON

_API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather_data():
    params = {
        "latitude": float(os.environ["WEATHER_LOCATION_LAT"]),
        "longitude": float(os.environ["WEATHER_LOCATION_LON"]),
        "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "timezone": os.environ["WEATHER_TIMEZONE"],
        "forecast_days": 1,
    }

    response = requests.get(_API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    with open(WEATHER_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    temp = data["current"]["temperature_2m"]
    code = data["current"]["weather_code"]
    print(f"Wrote {WEATHER_JSON} (temp={temp}°C, weather_code={code})")
