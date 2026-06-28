
<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD041 -->
<p align="center">
<img src="radio.png" alt="Radio"/>
</p>
<!-- markdownlint-enable MD041 -->

<h1 align="center" style="font-family: 'Courier New', monospace;">radio 0 7 9</h1>
<!-- markdownlint-enable MD033 -->

A tiny local radio station. Every day it generates a spoken weather greeting
for your location and stitches it together with the latest German news podcasts
into a continuous stream, served from a minimal "now playing" web page.

## What it plays

- **Weather greeting** — current conditions from [Open-Meteo](https://open-meteo.com/)
  turned into a short, mood-matched German greeting by an OpenAI-compatible LLM,
  then voiced with [Cartesia](https://cartesia.ai/) text-to-speech. The voice is
  picked at random and the emotion follows the forecast (cheerful in fair
  weather, more subdued in bad weather).
- **heise kurz informiert** — latest episode of the
  [podcast feed](https://kurzinformiert.podigee.io/feed/mp3).
- **tagesschau in 100 Sekunden** — latest episode of the
  [podcast feed](https://www.tagesschau.de/multimedia/sendung/tagesschau_in_100_sekunden/).
- **Jingles** — optional intro, outro, and between-track jingles dropped into
  `jingles/intro`, `jingles/outro`, and `jingles/random` (`.wav` only; a folder
  with no `.wav` files is simply skipped).

Generated audio is written under `data/YYYYMMDD/`. The weather greeting is only
created once per day, and date folders older than 7 days are cleaned up
automatically.

## Requirements

- Docker
- An OpenAI-compatible LLM provider (API key, base URL, model name) for the
  weather greeting text
- A [Cartesia](https://cartesia.ai/) account for text-to-speech
- `alsa-utils` (only for the `make play` target, which uses `aplay`)

## Configuration

Copy [.env.example](./.env.example) to `.env` and fill in the values:

| Variable | Description |
| --- | --- |
| `OPENAI_API_KEY` | API key for the OpenAI-compatible provider |
| `OPENAI_API_BASE_URL` | Provider API base URL |
| `OPENAI_MODEL` | LLM name used to write the greeting |
| `TTS_API_KEY` | Cartesia API key |
| `TTS_API_URL` | Cartesia TTS endpoint (`https://api.cartesia.ai/tts/bytes`) |
| `TTS_API_VERSION` | Cartesia API version |
| `TTS_MODEL_ID` | Cartesia model id (e.g. `sonic-3.5`) |
| `WEATHER_LOCATION_LAT` | Latitude of your location |
| `WEATHER_LOCATION_LON` | Longitude of your location |
| `WEATHER_LOCATION_ALIAS` | Friendly location name used in the greeting |
| `WEATHER_TIMEZONE` | IANA timezone, e.g. `Europe/London` |

## Usage

```sh
make help        # list all targets
make build       # build the Docker image
make run         # generate today's audio into ./data
make webserver   # build and stream on http://localhost:8079
make play        # play today's audio locally via aplay
make check       # run ruff and mypy
```

`make webserver` starts the streaming server. The web page polls until the
day's audio is ready, then plays the playlist (jingles, weather, news) on a
loop with pause and skip controls.

The image is tagged with the current version, derived from the latest git tag
via `git describe` (semver, `v` prefix stripped). The version is shown in the
web page footer.

## Bookmarks

- [Pi FM Kitchen Radio Station](https://github.com/trwmato/pi-fm-kitchen-radio/)
- [Podget](https://github.com/dvehrs/podget)
- Cartesia
  - [Cartesia Text-to-Speech API](https://docs.cartesia.ai/api-reference/tts/bytes)
  - [Cartesia MCP](https://docs.cartesia.ai/tools/ai/mcp)

## Sources

- [radio.png](./radio.png) is this [GitHub asset](https://github.githubassets.com/images/icons/emoji/unicode/1f4fb.png?v8)

## Disclaimer

- I used Claude and ChatGPT to realize this project.
- I don't speak Python, I don't like Python.
- I'm not responsible for external links.

---

<!-- markdownlint-disable MD033 -->
<p align="center">
    <a href="https://lttl.dev/"><img alt="lttl.dev logo" src="logo.png"/></a>
</p>
