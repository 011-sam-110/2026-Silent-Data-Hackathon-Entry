"""
ESG Provenance Auditor — Streamlit UI
Enterprise Fintech compliance dashboard · Agentic AI + Blockchain layer

Run:
    pip install -r requirements.txt
    streamlit run app.py

Video background:
    On first launch this app hard-links
        media/14003675-uhd_3840_2160_60fps.mp4  →  static/bg-video.mp4
    automatically (no disk copy, instant).  If that fails (cross-volume /
    restricted permissions) copy the file manually:
        cp media/14003675-uhd_3840_2160_60fps.mp4 static/bg-video.mp4
"""

import hashlib
import os
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────────────────────
# STATIC VIDEO BOOTSTRAP
# Streamlit serves ./static/ at /app/static/ when enableStaticServing = true.
# A hard-link is instantaneous and takes no extra disk space (same volume req.)
# ─────────────────────────────────────────────────────────────────────────────
_SRC = os.path.join("media", "14003675-uhd_3840_2160_60fps.mp4")
_DST = os.path.join("static", "bg-video.mp4")

os.makedirs("static", exist_ok=True)
if os.path.exists(_SRC) and not os.path.exists(_DST):
    try:
        os.link(_SRC, _DST)
    except OSError:
        pass  # Cross-volume or restricted — copy manually (see docstring above)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  — must be the first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG Provenance Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND VIDEO
# Injected via components.html so the element lands directly on document.body.
# This bypasses Streamlit's stacking-context containers, which would otherwise
# trap a position:fixed element and prevent it from covering the full viewport.
# The guard `if (pd.getElementById("esg-bg")) return;` makes this idempotent
# across Streamlit script re-runs.
# ─────────────────────────────────────────────────────────────────────────────
components.html(
    """
    <script>
    (function () {
        var pd = window.parent.document;

        /* Run once only — survives Streamlit re-runs */
        if (pd.getElementById("esg-bg")) return;

        /* ── CSS injected into the parent page head ── */
        var s = pd.createElement("style");
        s.id = "esg-bg-style";
        s.textContent = [
            "html{background:#040d1f!important}",
            "body{background:transparent!important}",
            "#root,.stApp,[data-testid='stAppViewContainer']",
            ",[data-testid='stAppViewContainer']>.main",
            ",[data-testid='stHeader']+div,[data-testid='stBottom']",
            ",.main,.block-container{background:transparent!important}",
            "#root{position:relative!important;z-index:1!important}",
            "#esg-bg{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none}",
            "#esg-vid{width:100%;height:100%;object-fit:cover;",
            "opacity:.35;filter:saturate(.6) brightness(.75)}",
            "#esg-veil{position:absolute;inset:0;background:linear-gradient(",
            "150deg,rgba(4,13,31,.45) 0%,rgba(4,13,31,.32) 5%,rgba(2,10,28,.50) 100%)}"
        ].join("");
        pd.head.appendChild(s);

        /* ── Video element prepended to body ── */
        var bg = pd.createElement("div");
        bg.id = "esg-bg";
        var vid = pd.createElement("video");
        vid.id = "esg-vid";
        vid.autoplay = true;
        vid.muted = true;
        vid.loop = true;
        vid.setAttribute("playsinline", "");
        var src = pd.createElement("source");
        src.src = window.parent.location.origin + "/app/static/bg-video.mp4";
        src.type = "video/mp4";
        vid.appendChild(src);
        var veil = pd.createElement("div");
        veil.id = "esg-veil";
        bg.appendChild(vid);
        bg.appendChild(veil);
        pd.body.insertBefore(bg, pd.body.firstChild);
        vid.play().catch(function(){});
    })();
    </script>
    """,
    height=0,
    scrolling=False,
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# Fonts: Syne (display) · Figtree (body) · JetBrains Mono (code/hash)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Figtree:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* ── Tokens ─────────────────────────────────────────────────────────── */
    :root {
        --bg:          #040d1f;
        --surface:     rgba(6, 17, 42, 0.90);
        --border:      rgba(0, 229, 160, 0.16);
        --border-hi:   rgba(0, 229, 160, 0.36);
        --accent:      #00e5a0;
        --accent-glow: rgba(0, 229, 160, 0.26);
        --blue:        #1d6af5;
        --text-hi:     #eef2f7;
        --text-mid:    #8fa3bf;
        --text-lo:     #4d6480;
        --pass:        #22c55e;
        --warn:        #f59e0b;
        --fail:        #ef4444;
        --f-display:   'Syne', sans-serif;
        --f-body:      'Figtree', sans-serif;
        --f-mono:      'JetBrains Mono', monospace;
    }

    /* ── Background video ───────────────────────────────────────────────── */
    #esg-bg {
        position: fixed; inset: 0; z-index: 0; overflow: hidden;
    }
    #esg-vid {
        width: 100%; height: 100%;
        object-fit: cover;
        opacity: 0.35;
        filter: saturate(0.6) brightness(0.75);
    }
    #esg-veil {
        position: absolute; inset: 0;
        background: linear-gradient(
            150deg,
            rgba(4, 13, 31, 0.45) 0%,
            rgba(4, 13, 31, 0.32) 55%,
            rgba(2, 10, 28, 0.50) 100%
        );
    }

    /* ── Streamlit shell ────────────────────────────────────────────────── */
    #root,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
        position: relative;
        z-index: 1;
    }
    [data-testid="stHeader"] {
        background: rgba(4, 13, 31, 0.80) !important;
        border-bottom: 1px solid var(--border) !important;
        backdrop-filter: blur(14px);
    }
    .main .block-container {
        background: transparent !important;
        padding: 1.5rem 2.5rem 3rem !important;
        max-width: 1400px !important;
    }

    /* ── Base typography ────────────────────────────────────────────────── */
    body, p, span, label, div, li, td, th, input, select, textarea, button {
        font-family: var(--f-body);
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--f-display) !important;
        color: var(--text-hi) !important;
        letter-spacing: -0.025em;
    }
    p, label, span { color: var(--text-mid); }
    code, pre, kbd  { font-family: var(--f-mono) !important; }

    /* ── Hero ───────────────────────────────────────────────────────────── */
    .hero {
        text-align: center;
        padding: 4rem 3rem 3rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background: rgba(4, 13, 31, 0.42);
        border: 1px solid var(--border);
        border-bottom: none;
        border-radius: 20px 20px 0 0;
        margin-bottom: 0;
        position: relative; overflow: hidden;
    }
    /* Top accent line */
    .hero::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent 5%, var(--accent) 45%, #4af7d0 55%, transparent 95%);
        opacity: 0.75;
        z-index: 2;
    }
    /* Radial glow behind title */
    .hero::after {
        content: '';
        position: absolute; top: -10%; left: 50%; transform: translateX(-50%);
        width: 900px; height: 650px;
        background: radial-gradient(ellipse, rgba(0,229,160,0.08) 0%, transparent 58%);
        pointer-events: none;
        z-index: 0;
    }
    /* Corner brackets */
    .corner {
        position: absolute; width: 22px; height: 22px; opacity: 0.55; z-index: 2;
    }
    .corner.tl { top: 16px;    left: 16px;  border-top:    1.5px solid var(--accent); border-left:  1.5px solid var(--accent); }
    .corner.tr { top: 16px;    right: 16px; border-top:    1.5px solid var(--accent); border-right: 1.5px solid var(--accent); }
    .corner.bl { bottom: 16px; left: 16px;  border-bottom: 1.5px solid var(--accent); border-left:  1.5px solid var(--accent); }
    .corner.br { bottom: 16px; right: 16px; border-bottom: 1.5px solid var(--accent); border-right: 1.5px solid var(--accent); }
    /* Scan lines */
    .hero-scanlines {
        position: absolute; inset: 0;
        background: repeating-linear-gradient(
            0deg, transparent, transparent 3px,
            rgba(0,229,160,0.012) 3px, rgba(0,229,160,0.012) 4px
        );
        pointer-events: none; border-radius: 20px; z-index: 1;
    }
    /* Sweep beam */
    .hero-sweep {
        position: absolute; inset: 0; overflow: hidden;
        border-radius: 20px; pointer-events: none; z-index: 1;
    }
    .hero-sweep::after {
        content: '';
        position: absolute; left: 0; right: 0; height: 160px;
        background: linear-gradient(180deg,
            transparent,
            rgba(0,229,160,0.030) 40%,
            rgba(0,229,160,0.060) 50%,
            rgba(0,229,160,0.030) 60%,
            transparent);
        animation: scanbeam 14s linear infinite;
    }
    @keyframes scanbeam {
        0%   { top: -160px; }
        100% { top: calc(100vh + 160px); }
    }
    /* All hero content above overlays */
    .hero > *:not(.corner):not(.hero-scanlines):not(.hero-sweep) {
        position: relative; z-index: 3;
    }

    .hero-eyebrow {
        font-family: var(--f-mono) !important;
        font-size: 0.64rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--accent) !important;
        margin-bottom: 1.5rem;
        opacity: 0.80;
    }
    .hero-title {
        font-family: var(--f-display) !important;
        font-size: clamp(2.4rem, 5.5vw, 4rem);
        font-weight: 800;
        background: linear-gradient(115deg, var(--accent) 0%, #4af7d0 30%, var(--blue) 62%, var(--accent) 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.035em;
        line-height: 1.08;
        margin-bottom: 1.25rem;
        animation: shimmer 7s linear infinite;
    }
    @keyframes shimmer {
        0%   { background-position: 0%   center; }
        100% { background-position: 200% center; }
    }
    /* Terminal cursor blink */
    .cursor-blink {
        display: inline-block;
        width: 2.5px; height: 0.80em;
        background: var(--accent);
        vertical-align: middle;
        margin-left: 5px;
        border-radius: 1px;
        animation: cur-blink 1.15s step-end infinite;
    }
    @keyframes cur-blink {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0; }
    }
    .hero-sub {
        font-size: 1.05rem;
        color: var(--text-mid) !important;
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.72;
        font-weight: 400;
    }
    .badge-row {
        display: flex; justify-content: center;
        gap: 0.55rem; margin-top: 2.2rem; flex-wrap: wrap;
    }
    /* Staggered badge entrance */
    .badge-row .badge:nth-child(1) { animation: badge-in 0.5s 0.10s both; }
    .badge-row .badge:nth-child(2) { animation: badge-in 0.5s 0.20s both; }
    .badge-row .badge:nth-child(3) { animation: badge-in 0.5s 0.30s both; }
    .badge-row .badge:nth-child(4) { animation: badge-in 0.5s 0.40s both; }
    .badge-row .badge:nth-child(5) { animation: badge-in 0.5s 0.50s both; }
    .badge-row .badge:nth-child(6) { animation: badge-in 0.5s 0.60s both; }
    @keyframes badge-in {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .badge {
        font-family: var(--f-mono) !important;
        padding: 0.26rem 0.82rem;
        border-radius: 4px;
        font-size: 0.62rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .b-teal { background:rgba(0,229,160,0.08); border:1px solid rgba(0,229,160,0.28); color:var(--accent)  !important; }
    .b-blue { background:rgba(29,106,245,0.08); border:1px solid rgba(29,106,245,0.28); color:#60a5fa !important; }
    .b-purp { background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.28); color:#c084fc !important; }
    /* Scroll hint */
    .scroll-hint {
        position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%);
        display: flex; flex-direction: column; align-items: center; gap: 0.35rem;
        color: var(--text-lo) !important;
        font-family: var(--f-mono) !important;
        font-size: 0.58rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        opacity: 0.55;
        animation: bob 2.6s ease-in-out infinite;
        z-index: 3;
        white-space: nowrap;
    }
    .scroll-arrow {
        font-size: 1.0rem;
        color: var(--accent) !important;
        opacity: 0.75;
        line-height: 1;
    }
    @keyframes bob {
        0%, 100% { transform: translateX(-50%) translateY(0); }
        50%       { transform: translateX(-50%) translateY(6px); }
    }

    /* ── Dividers ───────────────────────────────────────────────────────── */
    hr { border-color: rgba(0,229,160,0.09) !important; margin: 1.75rem 0 !important; }

    /* ── Section labels ─────────────────────────────────────────────────── */
    .slabel {
        font-family: var(--f-mono) !important;
        font-size: 0.60rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.17em;
        color: var(--accent) !important;
        margin-bottom: 0.35rem;
        display: block;
    }

    /* ── File uploader ──────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: var(--surface) !important;
        border: 1px dashed rgba(0,229,160,0.24) !important;
        border-radius: 10px !important;
        transition: border-color 0.2s;
    }
    [data-testid="stFileUploader"]:focus-within,
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(0,229,160,0.50) !important;
    }
    [data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
    }

    /* ── Multiselect ────────────────────────────────────────────────────── */
    [data-testid="stMultiSelect"] > div > div {
        background: var(--surface) !important;
        border-color: rgba(0,229,160,0.20) !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: rgba(0,229,160,0.11) !important;
        color: var(--accent) !important;
        border: 1px solid rgba(0,229,160,0.28) !important;
        border-radius: 4px !important;
        font-size: 0.76rem !important;
    }

    /* ── Primary button ─────────────────────────────────────────────────── */
    [data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #00e5a0 0%, #00c07c 100%) !important;
        border: none !important;
        color: #030c1a !important;
        font-family: var(--f-display) !important;
        font-weight: 700 !important;
        font-size: 0.90rem !important;
        letter-spacing: 0.03em !important;
        padding: 0.65rem 1.4rem !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 22px var(--accent-glow) !important;
        transition: all 0.16s ease !important;
    }
    [data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 28px var(--accent-glow), 0 8px 28px var(--accent-glow) !important;
    }
    [data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(0) scale(0.97) !important;
    }

    /* ── Metrics ────────────────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 1.1rem 1.2rem !important;
        transition: border-color 0.2s;
    }
    [data-testid="metric-container"]:hover {
        border-color: var(--border-hi) !important;
    }
    /* Streamlit uses different test-ids across versions — target both */
    [data-testid="metric-container"] [data-testid="stMetricValue"],
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-family: var(--f-display) !important;
        color: var(--accent) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricLabel"],
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-family: var(--f-mono) !important;
        color: var(--text-lo) !important;
        font-size: 0.65rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.10em !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"],
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 0.73rem !important;
        font-weight: 600 !important;
    }

    /* ── Spinner ────────────────────────────────────────────────────────── */
    [data-testid="stSpinner"] > div {
        border-top-color: var(--accent) !important;
    }

    /* ── Error alert ────────────────────────────────────────────────────── */
    [data-testid="stAlert"] {
        background: rgba(239,68,68,0.07) !important;
        border: 1px solid rgba(239,68,68,0.24) !important;
        border-radius: 10px !important;
    }

    /* ── Audit table ────────────────────────────────────────────────────── */
    .audit-tbl {
        width: 100%;
        border-collapse: collapse;
        font-family: var(--f-body);
        font-size: 0.855rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    .audit-tbl th {
        text-align: left;
        padding: 0.72rem 1.1rem;
        background: rgba(0,229,160,0.07);
        color: var(--accent) !important;
        font-family: var(--f-mono) !important;
        font-size: 0.60rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        border-bottom: 1px solid var(--border);
        white-space: nowrap;
    }
    .audit-tbl td {
        padding: 0.72rem 1.1rem;
        color: var(--text-hi) !important;
        border-bottom: 1px solid rgba(255,255,255,0.03);
        vertical-align: middle;
        line-height: 1.5;
    }
    .audit-tbl tr:last-child td { border-bottom: none; }
    .audit-tbl tr:hover td      { background: rgba(0,229,160,0.022); }
    .audit-tbl td:nth-child(3)  {
        color: var(--text-mid) !important;
        font-size: 0.80rem;
        font-style: italic;
    }

    /* ── Status pills ───────────────────────────────────────────────────── */
    .sp { font-family: var(--f-mono) !important; font-size: .68rem; font-weight: 700;
          letter-spacing: .05em; padding: .18rem .55rem; border-radius: 4px; white-space: nowrap; }
    .sp-p { background:rgba(34,197,94,0.11);  color:#4ade80; border:1px solid rgba(34,197,94,0.26); }
    .sp-w { background:rgba(245,158,11,0.11); color:#fcd34d; border:1px solid rgba(245,158,11,0.26); }
    .sp-f { background:rgba(239,68,68,0.11);  color:#f87171; border:1px solid rgba(239,68,68,0.26); }

    /* ── Report header ──────────────────────────────────────────────────── */
    .report-bar {
        display: flex; align-items: center; gap: .9rem;
        margin-bottom: 1.5rem;
        padding: .85rem 1.1rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
    }
    .verified-chip {
        margin-left: auto;
        background: rgba(34,197,94,0.09);
        border: 1px solid rgba(34,197,94,0.26);
        color: #4ade80 !important;
        padding: .26rem .72rem;
        border-radius: 4px;
        font-family: var(--f-mono) !important;
        font-size: 0.63rem;
        font-weight: 500;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        animation: pulse-v 3s ease-in-out infinite;
    }
    @keyframes pulse-v {
        0%, 100% { box-shadow: 0 0 0   0 rgba(34,197,94,0.00); }
        50%       { box-shadow: 0 0 10px 2px rgba(34,197,94,0.16); }
    }

    /* ── Standards card ─────────────────────────────────────────────────── */
    .std-card {
        margin-top: 1rem;
        padding: .82rem 1rem;
        background: rgba(6,17,42,0.72);
        border: 1px solid rgba(0,229,160,0.11);
        border-radius: 8px;
    }
    .std-item {
        display: flex; align-items: center; gap: .45rem;
        padding: .2rem 0;
        color: var(--text-mid) !important;
        font-size: .8rem;
    }
    .std-dot {
        width: 4px; height: 4px;
        border-radius: 50%;
        background: var(--accent);
        flex-shrink: 0;
    }

    /* ── Blockchain verification ────────────────────────────────────────── */
    .chain-box {
        background: rgba(0,229,160,0.035);
        border: 1px solid rgba(0,229,160,0.20);
        border-radius: 14px;
        padding: 1.75rem 2rem;
        position: relative; overflow: hidden;
    }
    /* Top glow bar */
    .chain-box::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent 4%, var(--accent) 40%, #4af7d0 60%, transparent 96%);
    }
    /* Decorative corner grid */
    .chain-box::after {
        content: '';
        position: absolute; bottom: -24px; right: -24px;
        width: 140px; height: 140px;
        background:
            linear-gradient(rgba(0,229,160,0.055) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,229,160,0.055) 1px, transparent 1px);
        background-size: 18px 18px;
        pointer-events: none;
        border-radius: 4px;
    }
    .chain-title {
        display: flex; align-items: center; gap: .6rem;
        font-family: var(--f-display) !important;
        font-size: 1.0rem;
        font-weight: 700;
        color: var(--accent) !important;
        margin-bottom: 1.1rem;
    }
    .chain-grid {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1.5rem;
        align-items: center;
    }
    .hash-val {
        font-family: var(--f-mono) !important;
        font-size: .75rem;
        color: var(--accent) !important;
        word-break: break-all;
        background: rgba(0,0,0,.38);
        padding: .55rem .85rem;
        border-radius: 6px;
        border: 1px solid var(--border);
        line-height: 1.65;
    }
    .chain-status {
        margin-top: .8rem;
        font-size: .83rem;
        color: var(--text-mid) !important;
    }
    .chain-status strong { color: var(--accent) !important; font-weight: 600; }
    .chain-sub {
        margin-top: .28rem;
        font-family: var(--f-mono) !important;
        font-size: .70rem;
        color: var(--text-lo) !important;
    }
    .chain-link {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        background: rgba(0,229,160,0.08);
        border: 1px solid rgba(0,229,160,0.26);
        color: var(--accent) !important;
        padding: .55rem 1.2rem;
        border-radius: 8px;
        text-decoration: none !important;
        font-family: var(--f-display) !important;
        font-size: .82rem;
        font-weight: 600;
        transition: all 0.16s ease;
        white-space: nowrap;
    }
    .chain-link:hover {
        background: rgba(0,229,160,0.15);
        box-shadow: 0 4px 18px rgba(0,229,160,0.20);
        transform: translateY(-1px);
    }

    /* ── Results fade-up ────────────────────────────────────────────────── */
    .results {
        animation: fadeUp 0.45s cubic-bezier(.22,.68,0,1.2) both;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0);    }
    }

    /* ── Scrollbar ──────────────────────────────────────────────────────── */
    ::-webkit-scrollbar       { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: rgba(4,13,31,0.5); }
    ::-webkit-scrollbar-thumb { background: rgba(0,229,160,0.22); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,229,160,0.44); }

    /* ── Hero + input zone merged card ─────────────────────────────────── */
    .hero .corner.bl, .hero .corner.br { display: none !important; }
    .esg-input-zone {
        background: rgba(4, 13, 31, 0.42) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 20px 20px !important;
        padding: 1.5rem 1.5rem 3rem !important;
        margin-bottom: 2rem !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .esg-input-zone::before {
        content: '';
        position: absolute; bottom: 16px; left: 16px;
        width: 22px; height: 22px;
        border-bottom: 1.5px solid var(--accent);
        border-left: 1.5px solid var(--accent);
        opacity: 0.55; pointer-events: none; z-index: 2;
    }
    .esg-input-zone::after {
        content: '';
        position: absolute; bottom: 16px; right: 16px;
        width: 22px; height: 22px;
        border-bottom: 1.5px solid var(--accent);
        border-right: 1.5px solid var(--accent);
        opacity: 0.55; pointer-events: none; z-index: 2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero" id="esg-hero">
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="hero-scanlines"></div>
        <div class="hero-sweep"></div>
        <div class="hero-eyebrow">ESG Intelligence Platform &nbsp;·&nbsp; v2.0</div>
        <div class="hero-title">Decentralized ESG Auditor<span class="cursor-blink"></span></div>
        <p class="hero-sub">
            Verify corporate sustainability reports against global standards.<br>
            Powered by Agentic AI and Blockchain.
        </p>
        <div class="badge-row">
            <span class="badge b-teal">UN SDGs</span>
            <span class="badge b-teal">SASB</span>
            <span class="badge b-blue">TCFD</span>
            <span class="badge b-blue">GRI</span>
            <span class="badge b-purp">Blockchain Anchored</span>
            <span class="badge b-purp">Agentic AI</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# JS: tag the widget container so it visually merges with the hero card above
components.html(
    """
    <script>
    (function () {
        var pd = window.parent.document;

        function applyZone() {
            var blockContainer = pd.querySelector('.main .block-container');
            if (!blockContainer) return;
            var fileUploader = pd.querySelector('[data-testid="stFileUploader"]');
            if (!fileUploader) return;

            /* Walk up from the file uploader to a direct child of block-container */
            var el = fileUploader;
            while (el && el.parentElement !== blockContainer) {
                el = el.parentElement;
            }
            if (el && !el.classList.contains('esg-input-zone')) {
                el.classList.add('esg-input-zone');
            }
        }

        applyZone();
        setTimeout(applyZone, 300);

        var _t;
        new MutationObserver(function () {
            clearTimeout(_t);
            _t = setTimeout(applyZone, 80);
        }).observe(pd.body, { childList: true, subtree: true });
    })();
    </script>
    """,
    height=0,
    scrolling=False,
)

# ─────────────────────────────────────────────────────────────────────────────
# INPUT ZONE
# ─────────────────────────────────────────────────────────────────────────────
col_up, col_std = st.columns([1, 1], gap="medium")

with col_up:
    st.markdown('<span class="slabel">Sustainability Report</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type="pdf",
        label_visibility="collapsed",
    )

with col_std:
    st.markdown('<span class="slabel">Audit Framework</span>', unsafe_allow_html=True)
    standards = st.multiselect(
        "Standards",
        [
            "UN Sustainable Development Goals (SDGs)",
            "SASB Standards",
            "TCFD Recommendations",
            "GRI Standards",
            "Custom 'Green Token' Criteria",
        ],
        default=["SASB Standards"],
        label_visibility="collapsed",
    )

_, btn_col, _ = st.columns([1, 1, 1])
with btn_col:
    run_audit = st.button("⚡ Run AI Audit", type="primary", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS  (shown only after clicking Run AI Audit with a file uploaded)
# ─────────────────────────────────────────────────────────────────────────────
if run_audit and uploaded_file is not None:

    with st.spinner(
        "Agent analyzing PDF structure… extracting ESG metrics… verifying SASB compliance…"
    ):
        time.sleep(3)

    company = (
        uploaded_file.name.rsplit(".", 1)[0]
        .replace("_", " ")
        .replace("-", " ")
        .upper()
    )

    # ── Report header ──────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="results">
        <div class="report-bar">
            <div>
                <span class="slabel" style="margin-bottom:.18rem;">Audit Report</span>
                <div style="font-family:var(--f-display);font-size:1.35rem;font-weight:700;
                            color:var(--text-hi);letter-spacing:-.022em;">{company}</div>
            </div>
            <span class="verified-chip">✓ Verified</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m_col, d_col = st.columns([1, 2], gap="large")

    # ── Left: key metrics ──────────────────────────────────────────────────
    with m_col:
        st.markdown('<span class="slabel">Key Metrics</span>', unsafe_allow_html=True)
        st.metric("Overall Compliance Score", "82%",  "Highly Compliant")
        st.metric("Data Transparency Rating",  "A−",   "High")
        st.metric("Flagged Issues",             "2",    "−1 vs Last Year", delta_color="normal")

        stds_html = "".join(
            f'<div class="std-item"><span class="std-dot"></span>{s}</div>'
            for s in standards
        )
        st.markdown(
            f"""
            <div class="std-card">
                <span class="slabel" style="margin-bottom:.5rem;">Applied Standards</span>
                {stds_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Right: SASB compliance breakdown table ─────────────────────────────
    with d_col:
        st.markdown(
            '<span class="slabel">SASB Compliance Breakdown</span>',
            unsafe_allow_html=True,
        )

        _ROWS = [
            (
                "GHG Emissions (Scope 1 & 2)",
                "PASS",
                "'Total Scope 1 emissions reduced by 4%…' (p. 12)",
            ),
            (
                "Supply Chain Disclosure (Scope 3)",
                "PASS",
                "'…company disclosed comprehensive Scope 3 data…' (p. 15)",
            ),
            (
                "Water Management Protocols",
                "PARTIAL",
                "'Water risk assessments conducted, targets unclear…' (p. 22)",
            ),
            (
                "Renewable Energy Target (2030)",
                "FAIL",
                "No specific 2030 renewable energy target found in text.",
            ),
            (
                "Labor Practices Disclosure",
                "PASS",
                "'…all Tier 1 suppliers audited for labor compliance…' (p. 30)",
            ),
        ]

        _BADGE = {
            "PASS":    '<span class="sp sp-p">✅ PASS</span>',
            "PARTIAL": '<span class="sp sp-w">⚠️ PARTIAL</span>',
            "FAIL":    '<span class="sp sp-f">❌ FAIL</span>',
        }

        rows_html = ""
        for i, (crit, status, excerpt) in enumerate(_ROWS):
            stripe = "background:rgba(255,255,255,0.013);" if i % 2 == 0 else ""
            rows_html += f"""
            <tr style="{stripe}">
                <td>{crit}</td>
                <td style="text-align:center;">{_BADGE[status]}</td>
                <td>{excerpt}</td>
            </tr>"""

        st.markdown(
            f"""
            <table class="audit-tbl">
                <thead>
                    <tr>
                        <th>Audit Criteria</th>
                        <th style="text-align:center;">Status</th>
                        <th>AI Evidence Excerpt</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """,
            unsafe_allow_html=True,
        )

    # ── Blockchain verification footer ─────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    audit_hash   = hashlib.sha256(uploaded_file.name.encode()).hexdigest()
    stds_joined  = ", ".join(standards) if standards else "SASB Standards"

    st.markdown(
        f"""
        <div class="chain-box">
            <div class="chain-title">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="1.8"
                     stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                Blockchain Verification Layer
            </div>
            <div class="chain-grid">
                <div>
                    <span class="slabel" style="margin-bottom:.3rem;">Audit Hash (SHA-256)</span>
                    <div class="hash-val">{audit_hash}</div>
                    <div class="chain-status">
                        Status: <strong>Anchored to Silent Data (Applied Blockchain L2)</strong>
                    </div>
                    <div class="chain-sub">Standards applied: {stds_joined}</div>
                </div>
                <div>
                    <a href="#" class="chain-link">
                        🔗 View on Explorer
                    </a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif run_audit and uploaded_file is None:
    st.error("⚠️  Please upload a PDF sustainability report before running the audit.")
