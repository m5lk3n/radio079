import contextlib
import html
import random
import threading
import time
import wave
from pathlib import Path
from typing import cast

from flask import Flask, Response, jsonify, send_file

from config import is_weekend, today_paths
from heise.fetch_podcast import fetch_heise_podcast
from tagesschau.fetch_podcast import fetch_tagesschau_podcast
from weather.fetch_data import fetch_weather_data
from weather.generate_greeting_audio import generate_today_greeting_weather_audio
from weather.generate_text import generate_weather_text
from version import VERSION

app = Flask(__name__)

_state: dict[str, str] = {"phase": "creating"}
# sources whose audio could not be fetched/generated; replaced by a failure jingle
_failures: set[str] = set()
# current day's WAV paths per source, refreshed each generation cycle
_audio_paths: dict[str, str] = {}
_state_lock = threading.Lock()

# how often the running server re-checks the feeds (and the weekend status)
_REFRESH_INTERVAL_SECONDS = 3600

_RADIO_PNG = Path(__file__).parent.parent / "radio.png"
_JINGLES_ROOT = Path(__file__).parent.parent / "jingles"
_JINGLE_CATEGORIES = ("intro", "random", "outro", "always", "failure")
_GAP_SECONDS = 1.0  # pause between tracks
_OUTRO_EXTRA_GAP_SECONDS = 1.0  # additional pause after the outro before the loop repeats

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
  #status.failed { color: #cc4444; }
  #rotationLen { font-size: 0.75rem; color: #555; letter-spacing: 0.1rem; }
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
  #rotationWrap { position: relative; padding-bottom: 1.75rem; }
  #loopArrow {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: visible;
    pointer-events: none;
    color: #555;
  }
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
  .seg.failed .dot { border-color: #cc4444; }
  .seg.failed .label { color: #cc4444; }
  .seg.failed.active .dot {
    background: #cc4444;
    border-color: #cc4444;
    box-shadow: 0 0 0.5rem #cc4444;
  }
  .seg.failed.active .label { color: #cc4444; }
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
  <div id="rotationWrap">
    <svg id="loopArrow" aria-hidden="true">
      <defs>
        <marker id="loopHead" markerWidth="9" markerHeight="9" refX="5" refY="4" orient="auto">
          <path d="M1.2,1.2 L5.5,4 L1.2,6.8" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>
      <path id="loopPath" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-dasharray="3 3" marker-end="url(#loopHead)"/>
    </svg>
    <div id="rotation"></div>
  </div>
  <p id="rotationLen">&mdash;</p>
  <audio id="player"></audio>
  <footer>v__VERSION__</footer>
  <script>
    const GAP_MS = __GAP_MS__;
    const OUTRO_EXTRA_GAP_MS = __OUTRO_EXTRA_GAP_MS__;
    let tracks = [];
    let idx = 0;
    let started = false;
    const player = document.getElementById('player');
    const statusEl = document.getElementById('status');
    const rotationEl = document.getElementById('rotation');
    const rotationLenEl = document.getElementById('rotationLen');
    const rotationWrap = document.getElementById('rotationWrap');
    const loopPath = document.getElementById('loopPath');
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
    let playingIdx = 0;
    let segs = [];

    function buildRotation() {
      rotationEl.innerHTML = '';
      segs = tracks.map(t => {
        const seg = document.createElement('div');
        seg.className = 'seg' + (t.jingle ? ' jingle' : '') + (t.failed ? ' failed' : '');
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
      requestAnimationFrame(drawLoopArrow);
    }

    // Arc a dashed "repeat" arrow below the strip, from the last dot back into the first.
    function drawLoopArrow() {
      if (segs.length < 2) { loopPath.removeAttribute('d'); return; }
      const wrap = rotationWrap.getBoundingClientRect();
      const first = segs[0].querySelector('.dot').getBoundingClientRect();
      const last = segs[segs.length - 1].querySelector('.dot').getBoundingClientRect();
      const x1 = last.left + last.width / 2 - wrap.left;
      const x2 = first.left + first.width / 2 - wrap.left;
      const y1 = last.bottom - wrap.top + 2;
      const y2 = first.bottom - wrap.top + 2;
      // dip below the strip; taller arc for wider spans, but kept gentle
      const span = Math.abs(x1 - x2);
      const dropY = Math.max(y1, y2) + Math.max(12, Math.min(span * 0.18, 22));
      // pull control points inward so the curve enters/leaves at an angle,
      // letting the (orient=auto) arrowhead align with the curve instead of pointing straight up
      const k = Math.max(6, Math.min(span * 0.2, 28));
      loopPath.setAttribute('d',
        `M ${x1} ${y1} C ${x1 - k} ${dropY}, ${x2 + k} ${dropY}, ${x2} ${y2}`);
    }

    window.addEventListener('resize', drawLoopArrow);

    // jingles are picked at random each loop, so the length is approximate
    function showRotationLength(total) {
      if (!total) { rotationLenEl.textContent = ''; return; }
      const secs = Math.round(total);
      const m = Math.floor(secs / 60);
      const s = String(secs % 60).padStart(2, '0');
      rotationLenEl.textContent = '≈ ' + m + ':' + s + ' per rotation';
    }

    function highlightRotation(current) {
      segs.forEach((seg, i) => seg.classList.toggle('active', i === current));
    }

    function playNext() {
      if (gapTimer) { clearTimeout(gapTimer); gapTimer = null; }
      if (!tracks.length) return;
      const current = idx;
      playingIdx = current;
      const t = tracks[idx];
      idx = (idx + 1) % tracks.length;
      highlightRotation(current);
      if (t.failed) {
        statusEl.className = 'failed';
        statusEl.textContent = t.name + ': data unavailable';
      } else {
        statusEl.className = 'streaming';
        statusEl.textContent = 'now streaming: ' + t.name;
      }
      // cache-buster so jingles (incl. failure) get a fresh random pick each loop
      player.src = (t.jingle || t.failed) ? t.src + '?_=' + Date.now() : t.src;
      player.play().catch(console.error);
    }

    // pause between tracks, with an extra pause after the outro before the loop repeats
    function gapAfterPlaying() {
      const t = tracks[playingIdx];
      return GAP_MS + (t && t.outro ? OUTRO_EXTRA_GAP_MS : 0);
    }
    player.addEventListener('ended', () => { gapTimer = setTimeout(playNext, gapAfterPlaying()); });
    player.addEventListener('error', () => { gapTimer = setTimeout(playNext, gapAfterPlaying()); });

    function startPlayback() {
      if (started) return;
      started = true;
      fetch('/api/playlist')
        .then(r => r.json())
        .then(p => {
          tracks = p.tracks;
          idx = 0;
          buildRotation();
          showRotationLength(p.total);
          skipEl.disabled = false;
          pauseEl.disabled = false;
          playNext();
        })
        .catch(() => { started = false; });
    }

    // weekend: stop playback and clear the strip so the page can show the notice
    function suspendPlayback() {
      if (gapTimer) { clearTimeout(gapTimer); gapTimer = null; }
      player.pause();
      player.removeAttribute('src');
      player.load();
      started = false;
      tracks = [];
      idx = 0;
      rotationEl.innerHTML = '';
      segs = [];
      loopPath.removeAttribute('d');
      showRotationLength(0);
      skipEl.disabled = true;
      pauseEl.disabled = true;
    }

    // The server keeps fetching hourly and may flip into/out of the weekend
    // suspend while the page is open, so we poll continuously and react to
    // phase transitions (not just the initial load).
    let lastPhase = null;
    function poll() {
      fetch('/api/status')
        .then(r => r.json())
        .then(data => {
          const phase = data.phase;
          if (phase === 'suspended') {
            if (started || lastPhase !== 'suspended') suspendPlayback();
            statusEl.className = '';
            statusEl.textContent = 'back on monday...';
          } else if (phase === 'ready') {
            startPlayback();
          } else if (!started) {
            statusEl.className = '';
            statusEl.textContent = 'creating latest audio...';
          }
          lastPhase = phase;
          setTimeout(poll, started ? 60000 : 5000);
        })
        .catch(() => setTimeout(poll, 5000));
    }

    poll();
  </script>
</body>
</html>"""

_HTML = _HTML.replace("__VERSION__", html.escape(VERSION))
_HTML = _HTML.replace("__GAP_MS__", str(int(_GAP_SECONDS * 1000)))
_HTML = _HTML.replace("__OUTRO_EXTRA_GAP_MS__", str(int(_OUTRO_EXTRA_GAP_SECONDS * 1000)))


def _generate_once() -> None:
    # Suspend over the weekend: skip all fetching and let the page show a notice.
    if is_weekend():
        print("Weekend: suspending audio fetching until Monday")
        with _state_lock:
            _state["phase"] = "suspended"
        return

    paths = today_paths()
    audio_paths = {
        "weather": paths.weather_wav,
        "heise": paths.heise_wav,
        "tagesschau": paths.tagesschau_wav,
    }

    # On the first run (or coming back from the weekend) signal that audio is
    # being prepared; a steady-state refresh leaves "ready" untouched so an
    # already-playing page is not disrupted.
    with _state_lock:
        if _state["phase"] != "ready":
            _state["phase"] = "creating"

    # The weather greeting is generated once per day; the date-stamped path
    # changes at midnight, so a new day re-generates it.
    if not Path(paths.weather_wav).exists():
        try:
            fetch_weather_data(paths.weather_json)
            generate_weather_text(paths.weather_json, paths.weather_text_txt)
            generate_today_greeting_weather_audio(
                paths.weather_json, paths.weather_text_txt, paths.weather_wav, paths.weather_wav_raw
            )
        except Exception as e:
            print(f"Weather generation error: {e}")
    # Each source is fetched independently so one failure does not block the others.
    for name, fetch in (
        ("heise", lambda: fetch_heise_podcast(paths.heise_mp3, paths.heise_wav)),
        ("tagesschau", lambda: fetch_tagesschau_podcast(paths.tagesschau_mp3, paths.tagesschau_wav)),
    ):
        try:
            fetch()
        except Exception as e:
            print(f"{name} generation error: {e}")

    # A source counts as failed when its WAV is missing after the attempt; the
    # playlist then substitutes a failure jingle and the page flags it.
    failed = {name for name, path in audio_paths.items() if not Path(path).exists()}
    if failed:
        print(f"Sources unavailable, playing failure jingle for: {sorted(failed)}")
    with _state_lock:
        _audio_paths.clear()
        _audio_paths.update(audio_paths)
        _failures.clear()
        _failures.update(failed)
        _state["phase"] = "ready"


def _generate_loop() -> None:
    """Refresh audio on startup and then every hour for as long as the server runs."""
    while True:
        try:
            _generate_once()
        except Exception as e:
            print(f"Generation cycle error: {e}")
        time.sleep(_REFRESH_INTERVAL_SECONDS)


@app.route("/")
def index() -> tuple[str, int, dict[str, str]]:
    return _HTML, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/radio.png")
@app.route("/favicon.ico")
def radio_png():  # type: ignore[return]
    return send_file(str(_RADIO_PNG), mimetype="image/png")


@app.route("/audio/<source>")
def audio(source: str):  # type: ignore[return]
    with _state_lock:
        path = _audio_paths.get(source)
    if not path or not Path(path).exists():
        return "Not found", 404
    return send_file(path, mimetype="audio/wav", conditional=True)


def _jingle_files(category: str) -> list[Path]:
    """Return the .wav files in a jingle category folder (only .wav is supported)."""
    folder = _JINGLES_ROOT / category
    if not folder.is_dir():
        return []
    return sorted(folder.glob("*.wav"))


def _wav_duration(path: str | Path) -> float:
    """Length of a WAV in seconds, or 0.0 if it can't be read."""
    with contextlib.suppress(Exception), wave.open(str(path), "rb") as w:
        rate = w.getframerate()
        if rate:
            return w.getnframes() / rate
    return 0.0


def _jingle_avg_duration(category: str) -> float:
    """Average length of a category's jingles; jingles are picked at random each loop."""
    files = _jingle_files(category)
    if not files:
        return 0.0
    return sum(_wav_duration(f) for f in files) / len(files)


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
    with _state_lock:
        failures = set(_failures)
        audio_paths = dict(_audio_paths)
    tracks: list[dict[str, object]] = []

    def add_jingle(category: str) -> None:
        if _jingle_files(category):
            tracks.append({
                "src": f"/audio/jingle/{category}",
                "name": "jingle",
                "jingle": True,
                # the outro gets an extra pause before the loop repeats
                "outro": category == "outro",
                # random pick each loop, so the rotation length is an estimate
                "dur": _jingle_avg_duration(category),
            })

    def add_source(name: str) -> None:
        if name in failures:
            # source unavailable: play a random failure jingle in its place and flag it
            tracks.append({
                "src": "/audio/jingle/failure",
                "name": name,
                "failed": True,
                "dur": _jingle_avg_duration("failure"),
            })
        else:
            tracks.append({"src": f"/audio/{name}", "name": name, "dur": _wav_duration(audio_paths[name])})

    add_jingle("always")
    add_jingle("intro")
    add_source("weather")
    add_jingle("random")
    add_source("heise")
    add_jingle("always")
    add_jingle("random")
    add_source("tagesschau")
    add_jingle("outro")

    # one rotation = every track plus the 1 s gap that follows each before the loop
    # repeats, with an extra pause after the outro
    total = sum(cast(float, t["dur"]) for t in tracks) + len(tracks) * _GAP_SECONDS
    if any(t.get("outro") for t in tracks):
        total += _OUTRO_EXTRA_GAP_SECONDS
    return jsonify({"tracks": tracks, "total": total})


@app.route("/api/status")
def api_status():  # type: ignore[return]
    with _state_lock:
        return jsonify({"phase": _state["phase"]})


def run_webserver() -> None:
    threading.Thread(target=_generate_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8079, threaded=True)
