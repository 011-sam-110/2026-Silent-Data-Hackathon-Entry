"""
app.py -- Application entry point
AI Banking Compliance Auditor

Slim orchestrator that wires together configuration, styles, scripts,
and UI components. All heavy lifting lives in dedicated modules:

    config.py           Constants, page config, mock audit data
    helpers.py          load_css() / load_js() utilities
    components/
        hero.py         Hero banner HTML
        input_zone.py   File upload + framework selector + button
        results.py      Metrics, SASB table, blockchain verification

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os
from pathlib import Path

import streamlit as st

import config
from components import render_hero, render_input_zone, render_results
from helpers import load_css, load_js

# -----------------------------------------------------------------------
# VIDEO BOOTSTRAP
# Hard-link the source video into static/ so Streamlit can serve it.
# This runs at import time (before any Streamlit call) because it is
# pure filesystem work. Requires enableStaticServing = true in
# .streamlit/config.toml.
# -----------------------------------------------------------------------
_ROOT = Path(__file__).parent
_src = _ROOT / config.VIDEO_SRC
_dst = _ROOT / config.VIDEO_DST

os.makedirs(_dst.parent, exist_ok=True)
if _src.exists() and not _dst.exists():
    try:
        os.link(_src, _dst)
    except OSError:
        pass  # Cross-volume or restricted — copy the file manually

# -----------------------------------------------------------------------
# PAGE CONFIG — must be the very first st.* call
# -----------------------------------------------------------------------
st.set_page_config(**config.PAGE_CONFIG)

# -----------------------------------------------------------------------
# INJECT ASSETS
# Background video JS first, then all CSS in a single <style> tag
# (tokens.css must come first so :root vars are defined before use).
# -----------------------------------------------------------------------
load_js("scripts/bg_video.js")

load_css(
    "styles/tokens.css",
    "styles/shell.css",
    "styles/hero.css",
    "styles/forms.css",
    "styles/results.css",
    "styles/blockchain.css",
    "styles/chrome.css",
)

# -----------------------------------------------------------------------
# PAGE LAYOUT
# -----------------------------------------------------------------------
render_hero()
uploaded_file, standards, run_audit = render_input_zone()

if run_audit and uploaded_file is not None:
    render_results(uploaded_file, standards)
elif run_audit:
    st.error(
        "\u26a0\ufe0f  Please upload a PDF sustainability report "
        "before running the audit."
    )
