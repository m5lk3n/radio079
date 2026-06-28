import html
import random
import threading
from pathlib import Path

from flask import Flask, Response, jsonify, send_file

from config import HEISE_PODCAST_WAV, TAGESSCHAU_PODCAST_WAV, WEATHER_WAV
from heise.fetch_podcast import fetch_heise_podcast
from tagesschau.fetch_podcast import fetch_tagesschau_podcast
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text
from version import VERSION

app = Flask(__name__)

_state: dict[str, str] = {"phase": "creating"}
_state_lock = threading.Lock()

_RADIO_PNG = Path(__file__).parent.parent / "radio.png"
_JINGLES_ROOT = Path(__file__).parent.parent / "jingles"
_JINGLE_CATEGORIES = ("intro", "random", "outro", "always")

_HTML = """\
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>radio 0 7 9</title>
<link rel="icon" type="image/png" href="/radio.png">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #1a0f0a;
    color: #e0e0e0;
    font-family: 'Courier New', monospace;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    gap: 2rem;
  }
  img { width: 64px; height: 64px; image-rendering: pixelated; }
  h1 { font-size: 3rem; font-weight: normal; letter-spacing: 1rem; color: #fff; }
  #status { font-size: 0.9rem; color: #555; letter-spacing: 0.1rem; }
  #status.streaming { color: #44aaff; }
  #controls { display: flex; gap: 1rem; }
  .btn {
    font-family: inherit;
    font-size: 0.9rem;
    letter-spacing: 0.1rem;
    color: #e0e0e0;
    background: transparent;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 0.6rem 1.2rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: border-color 0.2s, color 0.2s;
  }
  .btn:hover:not(:disabled) { border-color: #44aaff; color: #44aaff; }
  .btn:disabled { opacity: 0.3; cursor: default; }
  .btn .icon { font-size: 1rem; line-height: 1; }
  #rotation {
    display: flex;
    align-items: flex-end;
    gap: 0.5rem;
    min-height: 2.5rem;
  }
  .seg {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
  }
  .seg .dot {
    width: 0.7rem;
    height: 0.7rem;
    border-radius: 50%;
    border: 1px solid #444;
    background: transparent;
    transition: background 0.3s, border-color 0.3s, box-shadow 0.3s;
  }
  .seg.jingle .dot { width: 0.4rem; height: 0.4rem; }
  .seg .label {
    font-size: 0.6rem;
    letter-spacing: 0.05rem;
    color: #555;
    transition: color 0.3s;
  }
  .seg.active .dot {
    background: #44aaff;
    border-color: #44aaff;
    box-shadow: 0 0 0.5rem #44aaff;
  }
  .seg.active .label { color: #44aaff; }
  footer {
    position: fixed;
    bottom: 0.75rem;
    font-size: 0.7rem;
    letter-spacing: 0.1rem;
    color: #444;
  }
  footer a { color: inherit; text-decoration: none; }
  footer a:hover { color: #44aaff; }
</style>
</head>
<body>
  <img src="/radio.png" alt="radio 0 7 9"/>
  <h1>radio 0 7 9</h1>
  <p id="status">&mdash;</p>
  <div id="controls">
    <button id="pause" class="btn" disabled><span class="icon" id="pauseIcon">&#9208;</span><span id="pauseLabel">pause</span></button>
    <button id="skip" class="btn" disabled><span class="icon">&#9197;</span>skip to next</button>
  </div>
  <div id="rotation"></div>
  <audio id="player"></audio>
  <footer>v__VERSION__</footer>
  <script>
    let tracks = [];
    let idx = 0;
    let started = false;
    const player = document.getElementById('player');
    const statusEl = document.getElementById('status');
    const rotationEl = document.getElementById('rotation');
    const skipEl = document.getElementById('skip');
    const pauseEl = document.getElementById('pause');
    const pauseIcon = document.getElementById('pauseIcon');
    const pauseLabel = document.getElementById('pauseLabel');

    skipEl.addEventListener('click', () => { if (started) playNext(); });
    pauseEl.addEventListener('click', () => {
      if (!started) return;
      if (player.paused) player.play().catch(console.error);
      else player.pause();
    });
    player.addEventListener('play', () => {
      pauseIcon.innerHTML = '&#9208;';
      pauseLabel.textContent = 'pause';
    });
    player.addEventListener('pause', () => {
      pauseIcon.innerHTML = '&#9654;';
      pauseLabel.textContent = 'play';
    });

    let gapTimer = null;
    let segs = [];

    function buildRotation() {
      rotationEl.innerHTML = '';
      segs = tracks.map(t => {
        const seg = document.createElement('div');
        seg.className = 'seg' + (t.jingle ? ' jingle' : '');
        seg.title = t.name;
        const dot = document.createElement('div');
        dot.className = 'dot';
        seg.appendChild(dot);
        if (!t.jingle) {
          const label = document.createElement('div');
          label.className = 'label';
          label.textContent = t.name;
          seg.appendChild(label);
        }
        rotationEl.appendChild(seg);
        return seg;
      });
    }

    function highlightRotation(current) {
      segs.forEach((seg, i) => seg.classList.toggle('active', i === current));
    }

    function playNext() {
      if (gapTimer) { clearTimeout(gapTimer); gapTimer = null; }
      if (!tracks.length) return;
      const current = idx;
      const t = tracks[idx];
      idx = (idx + 1) % tracks.length;
      highlightRotation(current);
      statusEl.className = 'streaming';
      statusEl.textContent = 'now streaming: ' + t.name;
      // cache-buster so jingles get a fresh random pick each loop
      player.src = t.jingle ? t.src + '?_=' + Date.now() : t.src;
      player.play().catch(console.error);
    }

    // one second pause between tracks
    player.addEventListener('ended', () => { gapTimer = setTimeout(playNext, 1000); });
    player.addEventListener('error', () => { gapTimer = setTimeout(playNext, 1000); });

    function poll() {
      fetch('/api/status')
        .then(r => r.json())
        .then(data => {
          if (data.phase === 'ready') {
            if (!started) {
              started = true;
              fetch('/api/playlist')
                .then(r => r.json())
                .then(p => {
                  tracks = p.tracks;
                  buildRotation();
                  skipEl.disabled = false;
                  pauseEl.disabled = false;
                  playNext();
                })
                .catch(() => { started = false; setTimeout(poll, 2000); });
            }
          } else {
            statusEl.textContent = 'creating latest audio...';
            setTimeout(poll, 2000);
          }
        })
        .catch(() => setTimeout(poll, 3000));
    }

    poll();
  </script>
</body>
</html>"""

_HTML = _HTML.replace("__VERSION__", html.escape(VERSION))


def _generate() -> None:
    try:
        if not Path(WEATHER_WAV).exists():
            fetch_weather_data()
            generate_weather_text()
            generate_today_greeting_weather_audio()
        fetch_heise_podcast()
        fetch_tagesschau_podcast()
    except Exception as e:
        print(f"Audio generation error: {e}")
    with _state_lock:
        _state["phase"] = "ready"


@app.route("/")
def index() -> tuple[str, int, dict[str, str]]:
    return _HTML, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/radio.png")
@app.route("/favicon.ico")
def radio_png():  # type: ignore[return]
    return send_file(str(_RADIO_PNG), mimetype="image/png")


_AUDIO_PATHS: dict[str, str] = {
    "weather": WEATHER_WAV,
    "heise": HEISE_PODCAST_WAV,
    "tagesschau": TAGESSCHAU_PODCAST_WAV,
}


@app.route("/audio/<source>")
def audio(source: str):  # type: ignore[return]
    path = _AUDIO_PATHS.get(source)
    if not path or not Path(path).exists():
        return "Not found", 404
    return send_file(path, mimetype="audio/wav", conditional=True)


def _jingle_files(category: str) -> list[Path]:
    """Return the .wav files in a jingle category folder (only .wav is supported)."""
    folder = _JINGLES_ROOT / category
    if not folder.is_dir():
        return []
    return sorted(folder.glob("*.wav"))


@app.route("/audio/jingle/<category>")
def jingle(category: str):  # type: ignore[return]
    if category not in _JINGLE_CATEGORIES:
        return "Not found", 404
    files = _jingle_files(category)
    if not files:
        return "Not found", 404
    resp = send_file(str(random.choice(files)), mimetype="audio/wav", conditional=False)
    resp.headers["Cache-Control"] = "no-store"  # pick a fresh random jingle each loop
    return resp


@app.route("/api/playlist")
def api_playlist() -> Response:
    """Ordered playlist with optional jingles inserted (omitted when a folder has no .wav)."""
    tracks: list[dict[str, object]] = []

    def add_jingle(category: str) -> None:
        if _jingle_files(category):
            tracks.append({"src": f"/audio/jingle/{category}", "name": "jingle", "jingle": True})

    add_jingle("always")
    add_jingle("intro")
    tracks.append({"src": "/audio/weather", "name": "weather"})
    add_jingle("random")
    tracks.append({"src": "/audio/heise", "name": "heise"})
    add_jingle("always")
    add_jingle("random")
    tracks.append({"src": "/audio/tagesschau", "name": "tagesschau"})
    add_jingle("outro")
    return jsonify({"tracks": tracks})


@app.route("/api/status")
def api_status():  # type: ignore[return]
    with _state_lock:
        return jsonify({"phase": _state["phase"]})


def run_webserver() -> None:
    threading.Thread(target=_generate, daemon=True).start()
    app.run(host="0.0.0.0", port=8079, threaded=True)
