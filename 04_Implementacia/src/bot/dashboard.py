"""
dashboard.py — Vinted Snajper Dashboard
========================================
Profesionálny webový dashboard pre správu Vinted Snajpera.

Spustenie:
    python dashboard.py
Potom otvor: http://<tvoja-IP>:5001
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
from collections import deque
from datetime import datetime
from functools import wraps
from pathlib import Path

import psutil
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for


# ---------------------------------------------------------------------------
# Konfigurácia
# ---------------------------------------------------------------------------

load_dotenv()

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_PATH    = BASE_DIR / "bot.log"
BOT_SCRIPT  = BASE_DIR / "vinted_scraper.py"
STATUS_PATH = BASE_DIR / "bot_status.json"

DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "vinted-snajper-secret-2024-xK9p")

MAX_LOG_LINES = 300

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ---------------------------------------------------------------------------
# In-memory log buffer
# ---------------------------------------------------------------------------

log_buffer: deque[str] = deque(maxlen=MAX_LOG_LINES)
_log_lock = threading.Lock()
_bot_process: subprocess.Popen | None = None
_log_reader_thread: threading.Thread | None = None


def _append_log(line: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    with _log_lock:
        log_buffer.append(f"[{ts}] {line.rstrip()}")


def _read_bot_stdout(proc: subprocess.Popen) -> None:
    try:
        for line in iter(proc.stdout.readline, b""):
            _append_log(line.decode("utf-8", errors="replace"))
    except Exception:
        pass


def _tail_log_file() -> None:
    import time
    try:
        with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            for line in lines[-MAX_LOG_LINES:]:
                _append_log(line)
            while True:
                line = f.readline()
                if line:
                    _append_log(line)
                else:
                    time.sleep(0.3)
    except FileNotFoundError:
        pass
    except Exception as e:
        _append_log(f"[dashboard] Chyba citania logu: {e}")


_file_tail_thread = threading.Thread(target=_tail_log_file, daemon=True)
_file_tail_thread.start()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"settings": {}, "searches": []}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)


def get_bot_pid() -> int | None:
    script_name = BOT_SCRIPT.name
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            if any(script_name in arg for arg in cmdline):
                return proc.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None


def is_bot_running() -> bool:
    global _bot_process
    if _bot_process is not None and _bot_process.poll() is None:
        return True
    return get_bot_pid() is not None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# HTML Template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="sk" data-bs-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vinted Snajper &mdash; Dashboard</title>
<meta name="description" content="Profesionalny dashboard pre spravu Vinted Snajper bota">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
<style>
  :root {
    --bg-primary:   #0e0a0f;
    --bg-secondary: #160f18;
    --bg-card:      #1d1320;
    --bg-card-2:    #221727;
    --border:       rgba(197,137,192,0.12);
    --accent:       #c589c0;
    --accent-glow:  rgba(197,137,192,0.22);
    --accent2:      #e0a8db;
    --green:        #22c55e;
    --red:          #ef4444;
    --text-muted:   #8b7a8a;
    --radius:       14px;
    --radius-sm:    8px;
    --font:         'Inter', system-ui, sans-serif;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: var(--font); background: var(--bg-primary); color: #e4e4e7; min-height: 100vh; }

  /* Navbar */
  .navbar-custom {
    background: rgba(22,15,24,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(197,137,192,0.18);
    padding: 0.75rem 1.5rem;
    position: sticky; top: 0; z-index: 1000;
  }
  .navbar-brand-text {
    font-size: 1.1rem; font-weight: 700;
    background: linear-gradient(135deg, #c589c0, #e0a8db);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .navbar-logo { height: 36px; width: 36px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
  .nav-badge { font-size: 0.65rem; font-weight: 600; padding: 2px 10px; border-radius: 20px; letter-spacing: 0.5px; text-transform: uppercase; }
  .badge-running { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
  .badge-stopped { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

  /* Cards */
  .card-custom { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; transition: border-color .2s, box-shadow .2s; }
  .card-custom:hover { border-color: rgba(197,137,192,0.35); box-shadow: 0 0 0 1px rgba(197,137,192,0.12), 0 4px 24px rgba(197,137,192,0.08); }
  .card-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }

  /* Stat chips */
  .stat-chip { background: var(--bg-card-2); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.25rem; }
  .stat-label { font-size: 0.72rem; color: var(--text-muted); font-weight: 500; }
  .stat-value { font-size: 1.6rem; font-weight: 700; letter-spacing: -1px; }
  .stat-sub   { font-size: 0.7rem; color: var(--text-muted); }

  /* Buttons */
  .btn-start { background: linear-gradient(135deg,#22c55e,#16a34a); border:none; color:#fff; font-weight:600; font-size:.85rem; padding:.6rem 1.4rem; border-radius:var(--radius-sm); transition:opacity .15s,transform .1s; display:inline-flex; align-items:center; gap:.5rem; cursor:pointer; }
  .btn-start:hover { opacity:.9; transform:translateY(-1px); color:#fff; }
  .btn-stop  { background: linear-gradient(135deg,#ef4444,#b91c1c); border:none; color:#fff; font-weight:600; font-size:.85rem; padding:.6rem 1.4rem; border-radius:var(--radius-sm); transition:opacity .15s,transform .1s; display:inline-flex; align-items:center; gap:.5rem; cursor:pointer; }
  .btn-stop:hover  { opacity:.9; transform:translateY(-1px); color:#fff; }
  .btn-accent { background: linear-gradient(135deg,#b06eab,#c589c0); border:none; color:#fff; font-weight:600; font-size:.82rem; padding:.55rem 1.25rem; border-radius:var(--radius-sm); transition:opacity .15s,transform .1s; display:inline-flex; align-items:center; gap:.4rem; cursor:pointer; }
  .btn-accent:hover { opacity:.88; transform:translateY(-1px); color:#fff; }
  .btn-icon { background: var(--bg-card-2); border:1px solid var(--border); color:var(--text-muted); padding:.3rem .55rem; border-radius:var(--radius-sm); font-size:.82rem; transition:all .15s; cursor:pointer; }
  .btn-icon:hover { color:#e8d5e7; border-color:rgba(197,137,192,0.3); }
  .btn-icon.danger:hover { color:var(--red); border-color:rgba(239,68,68,0.4); background:rgba(239,68,68,0.08); }

  /* Table */
  .table-custom { width:100%; border-collapse:separate; border-spacing:0 4px; }
  .table-custom thead th { font-size:.68rem; font-weight:600; letter-spacing:.8px; text-transform:uppercase; color:var(--text-muted); padding:0 1rem .6rem; border-bottom:1px solid var(--border); }
  .table-custom tbody tr { background:var(--bg-card-2); transition:background .15s; }
  .table-custom tbody tr:hover { background:rgba(197,137,192,0.07); }
  .table-custom tbody td { padding:.75rem 1rem; font-size:.875rem; border-top:1px solid var(--border); border-bottom:1px solid var(--border); }
  .table-custom tbody td:first-child { border-left:1px solid var(--border); border-radius:var(--radius-sm) 0 0 var(--radius-sm); }
  .table-custom tbody td:last-child  { border-right:1px solid var(--border); border-radius:0 var(--radius-sm) var(--radius-sm) 0; }
  .search-name { font-weight:600; color:#e8d5e7; }
  .search-url  { font-size:.75rem; color:var(--text-muted); max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; display:block; }
  .kw-badge { display:inline-block; font-size:.65rem; font-weight:500; padding:2px 8px; border-radius:20px; background:rgba(197,137,192,0.15); color:var(--accent2); border:1px solid rgba(197,137,192,0.25); margin:1px; }

  /* Terminal */
  .terminal { background:#09090b; border:1px solid var(--border); border-radius:var(--radius); padding:1rem 1.25rem; font-family:'SF Mono','Fira Code',Consolas,monospace; font-size:.78rem; line-height:1.6; color:#a1a1aa; height:380px; overflow-y:auto; }
  .log-line { display:block; white-space:pre-wrap; word-break:break-all; }
  .log-ts   { color:#52525b; margin-right:4px; }
  .log-info { color:#22d3ee; }
  .log-warn { color:#f59e0b; }
  .log-err  { color:#f87171; }
  .log-ok   { color:#86efac; }
  .terminal-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:.75rem; }
  .terminal-dot { width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:4px; }
  .dot-red{background:#ff5f56;} .dot-yellow{background:#ffbd2e;} .dot-green{background:#27c93f;}

  /* Modal */
  .modal-custom .modal-content { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius); }
  .modal-custom .modal-header { border-bottom:1px solid var(--border); }
  .modal-custom .modal-footer { border-top:1px solid var(--border); }
  .form-ctrl { background:var(--bg-primary); border:1px solid var(--border); border-radius:var(--radius-sm); color:#e8d5e7; font-size:.875rem; padding:.6rem .9rem; width:100%; transition:border-color .2s; font-family:var(--font); }
  .form-ctrl:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-glow); }
  .form-lbl { font-size:.75rem; font-weight:600; color:var(--text-muted); margin-bottom:.35rem; letter-spacing:.5px; text-transform:uppercase; display:block; }

  /* Toast */
  .toast-container { position:fixed; bottom:1.5rem; right:1.5rem; z-index:9999; display:flex; flex-direction:column; gap:.5rem; }
  .toast-custom { background:var(--bg-card-2); border:1px solid var(--border); border-radius:var(--radius-sm); padding:.75rem 1rem; font-size:.82rem; min-width:220px; animation:slideUp .25s ease; box-shadow:0 8px 32px rgba(0,0,0,0.4); }
  @keyframes slideUp { from{opacity:0;transform:translateY(12px);}to{opacity:1;transform:translateY(0);} }

  /* Login */
  .login-wrap { min-height:100vh; display:flex; align-items:center; justify-content:center; background:radial-gradient(ellipse at 50% 0%,rgba(197,137,192,0.14) 0%,transparent 60%),var(--bg-primary); }
  .login-card { background:var(--bg-card); border:1px solid rgba(197,137,192,0.18); border-radius:20px; padding:2.5rem 2rem; width:100%; max-width:380px; box-shadow:0 24px 64px rgba(0,0,0,0.6), 0 0 60px rgba(197,137,192,0.06); }
  .login-logo { display:flex; justify-content:center; margin-bottom:.75rem; }
  .login-logo img { width:72px; height:72px; border-radius:16px; object-fit:cover; box-shadow:0 8px 32px rgba(197,137,192,0.3); }
  .login-title { text-align:center; font-size:1.1rem; font-weight:700; margin-bottom:.25rem; background:linear-gradient(135deg,#c589c0,#e0a8db); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  .login-sub   { text-align:center; font-size:.8rem; color:var(--text-muted); margin-bottom:2rem; }

  /* Bot Status Panel */
  .status-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
  }
  .status-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    opacity: 0;
    transition: opacity .4s;
  }
  .status-panel.searching::before { opacity: 1; animation: scanBar 1.8s linear infinite; }
  @keyframes scanBar {
    0%   { background-position: -100% 0; }
    100% { background-position: 200% 0; }
  }
  .status-panel.searching { border-color: rgba(197,137,192,0.45); }
  .status-panel.sleeping  { border-color: rgba(245,158,11,0.3); }
  .status-panel.error     { border-color: rgba(239,68,68,0.4); }
  .status-panel.offline   { border-color: var(--border); }

  .sp-inner { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }
  .sp-icon  { font-size: 2.4rem; line-height:1; flex-shrink:0; }
  .sp-body  { flex: 1 1 auto; }
  .sp-label { font-size: .68rem; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: var(--text-muted); margin-bottom: .2rem; }
  .sp-main  { font-size: 1.35rem; font-weight: 700; letter-spacing: -.5px; color: #e4e4e7; line-height: 1.2; }
  .sp-sub   { font-size: .78rem; color: var(--text-muted); margin-top: .15rem; }

  /* Countdown block */
  .sp-countdown { display: flex; flex-direction: column; align-items: center; gap: .2rem; flex-shrink: 0; }
  .sp-cd-number { font-size: 3rem; font-weight: 800; letter-spacing: -2px; line-height: 1;
                  background: linear-gradient(135deg, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .sp-cd-label  { font-size: .6rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); }

  /* Progress bar */
  .sp-progress-wrap { flex: 1 1 120px; min-width: 100px; }
  .sp-progress-bar  { height: 6px; background: rgba(255,255,255,0.07); border-radius: 99px; overflow: hidden; margin-top: .5rem; }
  .sp-progress-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #f59e0b, #fbbf24);
                      transition: width .9s linear; }

  /* Blink dot for searching */
  .blink-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%;
               background: var(--accent); margin-right: 6px; box-shadow: 0 0 8px var(--accent);
               animation: blinkDot 1s step-start infinite; }
  @keyframes blinkDot { 0%,100%{opacity:1;} 50%{opacity:0;} }

  /* Misc */
  .pulse { animation:pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1;}50%{opacity:.45;} }
  .section-gap { margin-bottom:1.25rem; }
  .main-content { padding:1.75rem 1.5rem; max-width:1200px; margin:0 auto; }
  @media(max-width:768px){ .main-content{padding:1rem;} .stat-value{font-size:1.25rem;} }
</style>
</head>
<body>

{% if not session.authenticated %}
<!-- ══════════ LOGIN PAGE ══════════ -->
<div class="login-wrap">
  <div class="login-card">
    <div class="login-logo"><img src="/logo" alt="Vinted Snajper logo"></div>
    <div class="login-title">Vinted Snajper</div>
    <div class="login-sub">Dashboard &mdash; zadaj pristupove heslo</div>
    {% if error %}
    <div style="background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);color:#f87171;border-radius:8px;padding:.65rem .9rem;font-size:.82rem;margin-bottom:1rem;text-align:center;">
      <i class="bi bi-shield-x me-1"></i>Nespravne heslo
    </div>
    {% endif %}
    <form method="POST" action="/login">
      <div class="mb-3">
        <label class="form-lbl" for="password">Heslo</label>
        <input type="password" name="password" id="password" class="form-ctrl"
               placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;" autofocus autocomplete="current-password">
      </div>
      <button type="submit" class="btn-accent" style="width:100%;justify-content:center;padding:.75rem;">
        <i class="bi bi-unlock-fill"></i> Prihlasit sa
      </button>
    </form>
  </div>
</div>

{% else %}
<!-- ══════════ DASHBOARD ══════════ -->
<nav class="navbar-custom d-flex align-items-center justify-content-between">
  <div class="d-flex align-items-center gap-3">
    <img src="/logo" alt="Vinted Snajper" class="navbar-logo">
    <span class="navbar-brand-text">Vinted Snajper</span>
    <span class="nav-badge {% if bot_running %}badge-running{% else %}badge-stopped{% endif %}" id="nav-status-badge">
      {% if bot_running %}&#x1F7E2; BEZI{% else %}&#x1F534; STOJI{% endif %}
    </span>
  </div>
  <div class="d-flex align-items-center gap-3">
    <span style="font-size:.75rem;color:var(--text-muted);">{{ now }}</span>
    <a href="/logout" class="btn-icon" title="Odhlasit sa" style="text-decoration:none;">
      <i class="bi bi-box-arrow-right"></i>
    </a>
  </div>
</nav>

<div class="main-content">

  <!-- Stat chips -->
  <div class="row g-3 section-gap">
    <div class="col-6 col-md-3">
      <div class="stat-chip">
        <span class="stat-label"><i class="bi bi-search me-1"></i>Hladania</span>
        <span class="stat-value" style="color:var(--accent2);">{{ search_count }}</span>
        <span class="stat-sub">aktivnych vyhladavani</span>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-chip">
        <span class="stat-label"><i class="bi bi-activity me-1"></i>Stav bota</span>
        <span class="stat-value {% if bot_running %}pulse{% endif %}" id="stat-status"
              style="font-size:1.1rem;color:{% if bot_running %}var(--green){% else %}var(--red){% endif %};">
          {% if bot_running %}&#x25CF; AKTIVNY{% else %}&#x25CF; IDLE{% endif %}
        </span>
        <span class="stat-sub" id="bot-pid-info">{% if bot_pid %}PID: {{ bot_pid }}{% else %}Nespusteny{% endif %}</span>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-chip">
        <span class="stat-label"><i class="bi bi-clock me-1"></i>Interval</span>
        <span class="stat-value" style="color:#f59e0b;" id="stat-interval">{{ interval_min }}&ndash;{{ interval_max }}</span>
        <span class="stat-sub">sekund medzi cyklami</span>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="stat-chip">
        <span class="stat-label"><i class="bi bi-database me-1"></i>Databaza</span>
        <span class="stat-value" style="color:#22d3ee;">{{ db_size }}</span>
        <span class="stat-sub">vinted_bot.db</span>
      </div>
    </div>
  </div>

  <!-- Bot control -->
  <div class="card-custom section-gap">
    <div class="card-title"><i class="bi bi-terminal-fill"></i>Ovladanie bota</div>
    <div class="d-flex gap-2 flex-wrap align-items-center">
      <button class="btn-start" id="btn-start" onclick="botAction('start')"
        {% if bot_running %}disabled style="opacity:.4;cursor:not-allowed;"{% endif %}>
        <i class="bi bi-play-fill"></i> START
      </button>
      <button class="btn-stop" id="btn-stop" onclick="botAction('stop')"
        {% if not bot_running %}disabled style="opacity:.4;cursor:not-allowed;"{% endif %}>
        <i class="bi bi-stop-fill"></i> STOP
      </button>
      <button class="btn-icon ms-auto" onclick="refreshStatus()" title="Obnovit stav">
        <i class="bi bi-arrow-clockwise"></i> Obnovit
      </button>
    </div>
  </div>

  <!-- Searches + Log -->
  <div class="row g-3 section-gap">
    <div class="col-12 col-lg-7">
      <div class="card-custom h-100">
        <div class="card-title d-flex justify-content-between align-items-center w-100">
          <span><i class="bi bi-list-ul me-1"></i>Zoznam hladani</span>
          <button class="btn-accent" onclick="openAddModal()"><i class="bi bi-plus-lg"></i> Pridat</button>
        </div>
        <div style="overflow-x:auto;">
          <table class="table-custom" id="searches-table">
            <thead>
              <tr>
                <th>Nazov</th>
                <th>URL</th>
                <th>Klucove slova</th>
                <th style="text-align:right;">Akcie</th>
              </tr>
            </thead>
            <tbody id="searches-tbody">
              {% for s in searches %}
              <tr>
                <td><span class="search-name">{{ s.name }}</span></td>
                <td><span class="search-url" title="{{ s.url }}">{{ s.url }}</span></td>
                <td>
                  {% if s.keywords %}
                    {% for kw in s.keywords %}<span class="kw-badge">{{ kw }}</span>{% endfor %}
                  {% else %}
                    <span style="color:var(--text-muted);font-size:.75rem;">&mdash;</span>
                  {% endif %}
                </td>
                <td style="text-align:right;">
                  <button class="btn-icon me-1" title="Upravit"
                    onclick='openEditModal({{ loop.index0 }}, {{ s|tojson }})'>
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn-icon danger" title="Zmazat"
                    onclick="deleteSearch({{ loop.index0 }}, '{{ s.name|e }}')">
                    <i class="bi bi-trash3"></i>
                  </button>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
          {% if not searches %}
          <div style="text-align:center;padding:2rem;color:var(--text-muted);font-size:.85rem;">
            <i class="bi bi-inbox" style="font-size:2rem;display:block;margin-bottom:.5rem;"></i>
            Ziadne hladania. Klikni &bdquo;Pridat&ldquo;.
          </div>
          {% endif %}
        </div>
      </div>
    </div>

    <!-- Live Log -->
    <div class="col-12 col-lg-5">
      <div class="card-custom h-100">
        <div class="card-title d-flex justify-content-between align-items-center w-100">
          <span><i class="bi bi-terminal me-1"></i>Live Log</span>
          <div class="d-flex align-items-center gap-2">
            <span style="font-size:.65rem;color:var(--green);">&#x25CF; LIVE</span>
            <button class="btn-icon" onclick="clearLog()" title="Vycistit"><i class="bi bi-eraser"></i></button>
          </div>
        </div>

        <!-- ═══ Aktuálny stav bota ═══ -->
        <div class="status-panel offline" id="bot-status-panel">
          <div class="sp-inner">
            <div class="sp-icon" id="sp-icon">🔴</div>
            <div class="sp-body">
              <div class="sp-label">Aktuálny stav</div>
              <div class="sp-main" id="sp-main-text">Offline</div>
              <div class="sp-sub"  id="sp-sub-text">&nbsp;</div>
            </div>
            <div class="sp-countdown" id="sp-countdown-wrap" style="display:none;">
              <div class="sp-cd-number" id="sp-cd-number">--</div>
              <div class="sp-cd-label">sekúnd</div>
              <div class="sp-progress-wrap">
                <div class="sp-progress-bar"><div class="sp-progress-fill" id="sp-cd-bar" style="width:100%"></div></div>
              </div>
            </div>
          </div>
        </div>
        <!-- ═══ /Aktuálny stav ═══ -->

        <div class="terminal-header">
          <div>
            <span class="terminal-dot dot-red"></span>
            <span class="terminal-dot dot-yellow"></span>
            <span class="terminal-dot dot-green"></span>
          </div>
          <span style="font-size:.65rem;color:var(--text-muted);">bot.log &mdash; poslednych {{ max_log }} riadkov</span>
        </div>
        <div class="terminal" id="log-terminal">
          <span style="color:var(--text-muted);">Nacitavam logy...</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Settings -->
  <div class="card-custom section-gap">
    <div class="card-title"><i class="bi bi-gear-fill"></i>Nastavenia (config.json)</div>
    <form onsubmit="saveSettings(event)">
      <div class="row g-3">
        <div class="col-6 col-md-3">
          <label class="form-lbl" for="cfg-interval-min">Interval min (s)</label>
          <input type="number" id="cfg-interval-min" class="form-ctrl" value="{{ interval_min }}" min="5">
        </div>
        <div class="col-6 col-md-3">
          <label class="form-lbl" for="cfg-interval-max">Interval max (s)</label>
          <input type="number" id="cfg-interval-max" class="form-ctrl" value="{{ interval_max }}" min="5">
        </div>
        <div class="col-6 col-md-3">
          <label class="form-lbl" for="cfg-item-limit">Limit poloziek</label>
          <input type="number" id="cfg-item-limit" class="form-ctrl" value="{{ item_limit }}" min="1">
        </div>
        <div class="col-6 col-md-3 d-flex align-items-end">
          <button type="submit" class="btn-accent" style="width:100%;justify-content:center;">
            <i class="bi bi-floppy"></i> Ulozit
          </button>
        </div>
      </div>
    </form>
  </div>

</div>

<!-- Modal -->
<div class="modal fade modal-custom" id="searchModal" tabindex="-1" aria-labelledby="searchModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="searchModalLabel" style="font-size:.95rem;font-weight:700;">
          <i class="bi bi-search me-2"></i><span id="modal-title-text">Pridat hladanie</span>
        </h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <input type="hidden" id="modal-edit-index" value="-1">
        <div class="mb-3">
          <label class="form-lbl" for="modal-name">Nazov *</label>
          <input type="text" id="modal-name" class="form-ctrl" placeholder="napr. PS5, iPhone 13...">
        </div>
        <div class="mb-3">
          <label class="form-lbl" for="modal-url">Vinted URL *</label>
          <input type="text" id="modal-url" class="form-ctrl" placeholder="https://www.vinted.sk/catalog?search_text=...">
          <div style="font-size:.7rem;color:var(--text-muted);margin-top:.4rem;"><i class="bi bi-info-circle me-1"></i>Skopiruj URL priamo z Vinted vyhladavania</div>
        </div>
        <div class="mb-1">
          <label class="form-lbl" for="modal-keywords">Klucove slova (oddel ciarkou)</label>
          <input type="text" id="modal-keywords" class="form-ctrl" placeholder="napr. slim, 500GB, original">
          <div style="font-size:.7rem;color:var(--text-muted);margin-top:.4rem;"><i class="bi bi-info-circle me-1"></i>Volitelne &mdash; filtruje polozky s tymito slovami</div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-icon" data-bs-dismiss="modal">Zrusit</button>
        <button class="btn-accent" onclick="saveSearch()"><i class="bi bi-check-lg"></i> Ulozit</button>
      </div>
    </div>
  </div>
</div>

<div class="toast-container" id="toast-container"></div>
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function showToast(msg, color) {
  color = color || 'var(--accent)';
  const tc = document.getElementById('toast-container');
  if(!tc) return;
  const el = document.createElement('div');
  el.className = 'toast-custom';
  el.style.borderLeft = '3px solid ' + color;
  el.innerHTML = msg;
  tc.appendChild(el);
  setTimeout(function(){ el.style.opacity='0'; el.style.transition='opacity .3s'; setTimeout(function(){el.remove();},350); }, 3200);
}

async function botAction(action) {
  const btn = document.getElementById('btn-' + action);
  if(btn){ btn.disabled=true; btn.style.opacity='0.5'; }
  try {
    const res  = await fetch('/api/bot/' + action, {method:'POST'});
    const data = await res.json();
    showToast(data.message || action, data.ok ? 'var(--green)' : 'var(--red)');
    setTimeout(refreshStatus, 1200);
  } catch(e) {
    showToast('Chyba spojenia', 'var(--red)');
    if(btn){ btn.disabled=false; btn.style.opacity='1'; }
  }
}

async function refreshStatus() {
  try {
    const res  = await fetch('/api/status');
    const data = await res.json();
    const badge = document.getElementById('nav-status-badge');
    if(badge){ badge.className='nav-badge '+(data.running?'badge-running':'badge-stopped'); badge.innerHTML=data.running?'&#x1F7E2; BEZI':'&#x1F534; STOJI'; }
    const pidInfo = document.getElementById('bot-pid-info');
    if(pidInfo) pidInfo.textContent = data.pid ? 'PID: '+data.pid : 'Nespusteny';
    const statStatus = document.getElementById('stat-status');
    if(statStatus){ statStatus.style.color=data.running?'var(--green)':'var(--red)'; statStatus.innerHTML=data.running?'&#x25CF; AKTIVNY':'&#x25CF; IDLE'; statStatus.className='stat-value'+(data.running?' pulse':''); }
    const btnStart = document.getElementById('btn-start');
    const btnStop  = document.getElementById('btn-stop');
    if(btnStart){ btnStart.disabled=data.running; btnStart.style.opacity=data.running?'0.4':'1'; btnStart.style.cursor=data.running?'not-allowed':'pointer'; }
    if(btnStop) { btnStop.disabled=!data.running; btnStop.style.opacity=!data.running?'0.4':'1'; btnStop.style.cursor=!data.running?'not-allowed':'pointer'; }

    // ─── Bot Status Panel ───────────────────────────────────────────────────
    updateBotStatusPanel(data);
  } catch(e){}
}

// ─── Bot Status Panel logic ─────────────────────────────────────────────────
var _cdTotal    = null;  // sekundy celkovej pauzy
var _cdDeadline = null;  // unix timestamp (ms) kedy bude ďalší štart

function updateBotStatusPanel(data) {
  const panel  = document.getElementById('bot-status-panel');
  const icon   = document.getElementById('sp-icon');
  const main   = document.getElementById('sp-main-text');
  const sub    = document.getElementById('sp-sub-text');
  const cdWrap = document.getElementById('sp-countdown-wrap');
  if(!panel) return;

  // Zmaž všetky state triedy
  panel.classList.remove('searching','sleeping','error','offline');

  const bs = data.bot_status || {};
  const status = bs.status || (data.running ? 'Running' : 'Offline');

  if(!data.running || status === 'Stopped' || status === 'Offline') {
    panel.classList.add('offline');
    icon.textContent  = '🔴';
    main.textContent  = 'Offline';
    sub.textContent   = 'Bot momentálne nebeží';
    cdWrap.style.display = 'none';
    _cdDeadline = null;
    return;
  }

  if(status === 'Searching') {
    panel.classList.add('searching');
    icon.innerHTML = '<span class="blink-dot"></span>🔍';
    const task = bs.current_task || 'neznáma';
    main.innerHTML  = 'Práve hľadám: <span style="color:var(--accent2);">' + task + '</span>';
    sub.textContent = 'Aktívne skenovanie Vinted.sk';
    cdWrap.style.display = 'none';
    _cdDeadline = null;
    return;
  }

  if(status === 'Sleeping') {
    panel.classList.add('sleeping');
    icon.textContent = '😴';
    if(bs.next_run_at && bs.next_run_in) {
      _cdDeadline = bs.next_run_at * 1000;   // konvertuj na ms
      _cdTotal    = bs.next_run_in;
    }
    main.textContent = 'Čakám na ďalší cyklus';
    sub.textContent  = bs.current_task || 'Pauza medzi skenmi';
    cdWrap.style.display = 'flex';
    _tickCountdown();  // okamžite vykresli
    return;
  }

  if(status === 'Starting') {
    panel.classList.add('searching');
    icon.textContent  = '🚀';
    main.textContent  = 'Štartujem...';
    sub.textContent   = bs.current_task || 'Inicializácia';
    cdWrap.style.display = 'none';
    return;
  }

  if(status === 'Error') {
    panel.classList.add('error');
    icon.textContent  = '⚠️';
    main.textContent  = 'Chyba';
    sub.textContent   = bs.current_task || 'Nastala chyba';
    cdWrap.style.display = 'none';
    return;
  }
}

function _tickCountdown() {
  const cdNum = document.getElementById('sp-cd-number');
  const cdBar = document.getElementById('sp-cd-bar');
  if(!cdNum || !_cdDeadline) return;
  const remaining = Math.max(0, Math.ceil((_cdDeadline - Date.now()) / 1000));
  cdNum.textContent = remaining;
  if(cdBar && _cdTotal) {
    const pct = Math.min(100, (remaining / _cdTotal) * 100);
    cdBar.style.width = pct + '%';
  }
}

// Každú sekundu tikáme countdown aj refreshujeme status
setInterval(function(){
  _tickCountdown();
}, 1000);
setInterval(refreshStatus, 5000);

// Live log
let lastLogLen = 0;
const terminal = document.getElementById('log-terminal');

function colorize(line) {
  const esc = line.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const ts  = esc.match(/^\[\d{1,2}:\d{2}:\d{2}\]/);
  let body  = ts ? esc.slice(ts[0].length) : esc;
  let cls   = '';
  if(/ERROR|CHYBA|error|exception/i.test(body))   cls='log-err';
  else if(/WARNING|WARN|warn/i.test(body))         cls='log-warn';
  else if(/OK|SUCCESS|Najdena|Posiela|Odoslan/i.test(body)) cls='log-ok';
  else if(/INFO|info|Kontrolujem|Nacitav|Start|Spusten/i.test(body)) cls='log-info';
  const tsHtml = ts ? '<span class="log-ts">'+ts[0]+'</span>' : '';
  return '<span class="log-line '+cls+'">'+tsHtml+body+'</span>';
}

async function fetchLogs() {
  try {
    const res  = await fetch('/api/logs');
    const data = await res.json();
    if(!terminal) return;
    if(data.lines.length !== lastLogLen) {
      lastLogLen = data.lines.length;
      terminal.innerHTML = data.lines.map(colorize).join('') || '<span style="color:var(--text-muted);">Ziadne logy...</span>';
      terminal.scrollTop = terminal.scrollHeight;
    }
  } catch(e){}
}

function clearLog() {
  fetch('/api/logs/clear',{method:'POST'}).then(function(){ lastLogLen=0; if(terminal) terminal.innerHTML='<span style="color:var(--text-muted);">Log vycisteny.</span>'; });
}

fetchLogs();
setInterval(fetchLogs, 2000);

// CRUD
var searchModal = null;
document.addEventListener('DOMContentLoaded', function(){
  var el = document.getElementById('searchModal');
  if(el) searchModal = new bootstrap.Modal(el);
});

function openAddModal() {
  document.getElementById('modal-title-text').textContent = 'Pridat hladanie';
  document.getElementById('modal-edit-index').value = -1;
  document.getElementById('modal-name').value = '';
  document.getElementById('modal-url').value = '';
  document.getElementById('modal-keywords').value = '';
  if(searchModal) searchModal.show();
}

function openEditModal(idx, search) {
  document.getElementById('modal-title-text').textContent = 'Upravit hladanie';
  document.getElementById('modal-edit-index').value = idx;
  document.getElementById('modal-name').value = search.name || '';
  document.getElementById('modal-url').value = search.url || '';
  document.getElementById('modal-keywords').value = (search.keywords||[]).join(', ');
  if(searchModal) searchModal.show();
}

async function saveSearch() {
  const idx  = parseInt(document.getElementById('modal-edit-index').value);
  const name = document.getElementById('modal-name').value.trim();
  const url  = document.getElementById('modal-url').value.trim();
  const kwRaw= document.getElementById('modal-keywords').value.trim();
  const keywords = kwRaw ? kwRaw.split(',').map(function(k){return k.trim();}).filter(Boolean) : [];
  if(!name || !url){ showToast('<i class="bi bi-exclamation-triangle me-1"></i>Vyplň nazov a URL','var(--red)'); return; }
  const body     = {name,url,keywords};
  const endpoint = idx>=0 ? '/api/searches/'+idx : '/api/searches';
  const method   = idx>=0 ? 'PUT' : 'POST';
  try {
    const res  = await fetch(endpoint,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data = await res.json();
    if(data.ok){ showToast('<i class="bi bi-check-circle me-1"></i>'+(idx>=0?'Hladanie upravene':'Hladanie pridane'),'var(--green)'); if(searchModal)searchModal.hide(); setTimeout(function(){location.reload();},600); }
    else showToast(data.error||'Chyba ulozenia','var(--red)');
  } catch(e){ showToast('Chyba spojenia','var(--red)'); }
}

async function deleteSearch(idx, name) {
  if(!confirm('Naozaj zmazat "'+name+'"?')) return;
  try {
    const res  = await fetch('/api/searches/'+idx,{method:'DELETE'});
    const data = await res.json();
    if(data.ok){ showToast('<i class="bi bi-trash3 me-1"></i>Hladanie zmazane','var(--red)'); setTimeout(function(){location.reload();},500); }
  } catch(e){ showToast('Chyba spojenia','var(--red)'); }
}

async function saveSettings(e) {
  e.preventDefault();
  const body = {
    interval_min: parseInt(document.getElementById('cfg-interval-min').value),
    interval_max: parseInt(document.getElementById('cfg-interval-max').value),
    item_limit:   parseInt(document.getElementById('cfg-item-limit').value),
  };
  try {
    const res  = await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data = await res.json();
    showToast(data.ok?'<i class="bi bi-floppy me-1"></i>Nastavenia ulozene':(data.error||'Chyba'), data.ok?'var(--accent)':'var(--red)');
    if(data.ok){
      const imin = document.getElementById('cfg-interval-min').value;
      const imax = document.getElementById('cfg-interval-max').value;
      const si   = document.getElementById('stat-interval');
      if(si) si.textContent = imin + '\u2013' + imax;
    }
  } catch(e){ showToast('Chyba spojenia','var(--red)'); }
}
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Routes — Static assets
# ---------------------------------------------------------------------------


@app.route("/logo")
def serve_logo():
    from flask import send_from_directory
    return send_from_directory(str(BASE_DIR), "vinted snajper.png", mimetype="image/png")


# ---------------------------------------------------------------------------
# Routes — Auth
# ---------------------------------------------------------------------------


@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if not DASHBOARD_PASSWORD:
            error = True
        elif pwd == DASHBOARD_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("index"))
        else:
            error = True
    return render_template_string(
        HTML_TEMPLATE,
        error=error,
        bot_running=False,
        searches=[],
        search_count=0,
        interval_min=20,
        interval_max=40,
        item_limit=10,
        db_size="—",
        bot_pid=None,
        max_log=MAX_LOG_LINES,
        now="",
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Routes — Dashboard
# ---------------------------------------------------------------------------


@app.route("/")
@login_required
def index():
    cfg = load_config()
    searches = cfg.get("searches", [])
    settings = cfg.get("settings", {})

    db_path = BASE_DIR / settings.get("db_path", "vinted_bot.db")
    if db_path.exists():
        db_bytes = db_path.stat().st_size
        db_size = f"{db_bytes/1024:.0f} KB" if db_bytes < 1_048_576 else f"{db_bytes/1_048_576:.1f} MB"
    else:
        db_size = "N/A"

    return render_template_string(
        HTML_TEMPLATE,
        error=False,
        searches=searches,
        search_count=len(searches),
        bot_running=is_bot_running(),
        bot_pid=get_bot_pid(),
        interval_min=settings.get("check_interval_min", 20),
        interval_max=settings.get("check_interval_max", 40),
        item_limit=settings.get("item_limit", 10),
        db_size=db_size,
        max_log=MAX_LOG_LINES,
        now=datetime.now().strftime("%d.%m.%Y %H:%M"),
    )


# ---------------------------------------------------------------------------
# API — Bot control
# ---------------------------------------------------------------------------


@app.route("/api/status")
@login_required
def api_status():
    bot_status: dict = {}
    try:
        if STATUS_PATH.exists():
            with open(STATUS_PATH, encoding="utf-8") as f:
                bot_status = json.load(f)
    except Exception:
        pass
    return jsonify({
        "running":    is_bot_running(),
        "pid":        get_bot_pid(),
        "bot_status": bot_status,
    })


@app.route("/api/bot/start", methods=["POST"])
@login_required
def api_bot_start():
    global _bot_process, _log_reader_thread
    if is_bot_running():
        return jsonify({"ok": False, "message": "Bot uz bezi."})
    try:
        _append_log("▶ Spustam vinted_scraper.py...")
        _bot_process = subprocess.Popen(
            [sys.executable, str(BOT_SCRIPT)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        _log_reader_thread = threading.Thread(
            target=_read_bot_stdout, args=(_bot_process,), daemon=True
        )
        _log_reader_thread.start()
        return jsonify({"ok": True, "message": f"Bot spusteny (PID {_bot_process.pid})"})
    except Exception as e:
        return jsonify({"ok": False, "message": f"Chyba: {e}"})


@app.route("/api/bot/stop", methods=["POST"])
@login_required
def api_bot_stop():
    global _bot_process
    pid = get_bot_pid()
    stopped = False

    if _bot_process is not None and _bot_process.poll() is None:
        try:
            _bot_process.terminate()
            _bot_process.wait(timeout=5)
        except Exception:
            try:
                _bot_process.kill()
            except Exception:
                pass
        stopped = True
        _bot_process = None

    if pid:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=5)
            stopped = True
        except Exception:
            pass

    if stopped:
        _append_log("■ Bot zastaveny dashboardom.")
        return jsonify({"ok": True, "message": "Bot zastaveny"})
    return jsonify({"ok": False, "message": "Bot nebezi."})


# ---------------------------------------------------------------------------
# API — Logs
# ---------------------------------------------------------------------------


@app.route("/api/logs")
@login_required
def api_logs():
    with _log_lock:
        lines = list(log_buffer)
    return jsonify({"lines": lines})


@app.route("/api/logs/clear", methods=["POST"])
@login_required
def api_logs_clear():
    with _log_lock:
        log_buffer.clear()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API — CRUD Searches
# ---------------------------------------------------------------------------


@app.route("/api/searches", methods=["POST"])
@login_required
def api_search_add():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    keywords = data.get("keywords", [])
    if not name or not url:
        return jsonify({"ok": False, "error": "Chyba nazov alebo URL"})
    cfg = load_config()
    cfg.setdefault("searches", []).append({"name": name, "url": url, "keywords": keywords})
    save_config(cfg)
    _append_log(f"+ Pridane hladanie: {name}")
    return jsonify({"ok": True})


@app.route("/api/searches/<int:idx>", methods=["PUT"])
@login_required
def api_search_update(idx: int):
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    keywords = data.get("keywords", [])
    if not name or not url:
        return jsonify({"ok": False, "error": "Chyba nazov alebo URL"})
    cfg = load_config()
    searches = cfg.get("searches", [])
    if idx < 0 or idx >= len(searches):
        return jsonify({"ok": False, "error": "Neplatny index"})
    searches[idx] = {"name": name, "url": url, "keywords": keywords}
    save_config(cfg)
    _append_log(f"✎ Upravene hladanie #{idx}: {name}")
    return jsonify({"ok": True})


@app.route("/api/searches/<int:idx>", methods=["DELETE"])
@login_required
def api_search_delete(idx: int):
    cfg = load_config()
    searches = cfg.get("searches", [])
    if idx < 0 or idx >= len(searches):
        return jsonify({"ok": False, "error": "Neplatny index"})
    removed = searches.pop(idx)
    save_config(cfg)
    _append_log(f"✗ Zmazane hladanie: {removed.get('name','?')}")
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API — Settings
# ---------------------------------------------------------------------------


@app.route("/api/settings", methods=["POST"])
@login_required
def api_settings_save():
    data = request.get_json(silent=True) or {}
    cfg = load_config()
    settings = cfg.setdefault("settings", {})
    if "interval_min" in data:
        settings["check_interval_min"] = int(data["interval_min"])
    if "interval_max" in data:
        settings["check_interval_max"] = int(data["interval_max"])
    if "item_limit" in data:
        settings["item_limit"] = int(data["item_limit"])
    save_config(cfg)
    _append_log(
        f"Nastavenia ulozene: interval {settings.get('check_interval_min')}–{settings.get('check_interval_max')}s"
    )
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not DASHBOARD_PASSWORD:
        print(
            "\n⚠️  UPOZORNENIE: DASHBOARD_PASSWORD nie je nastavene v .env!\n"
            "   Pridaj do .env: DASHBOARD_PASSWORD=tvoje_heslo\n"
            "   Dashboard je momentalne neprístupny (vyzaduje heslo).\n"
        )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
