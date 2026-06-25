"""
components/hero.py -- Hero banner section
AI Banking Compliance Auditor

Renders the full-width hero banner with animated gradient title,
capability badges, corner brackets, and scanline overlay.
Static HTML injected via st.markdown.
"""

import streamlit as st

_HERO_HTML = """\
<div class="hero" id="esg-hero">
    <div class="corner tl"></div>
    <div class="corner tr"></div>
    <div class="hero-dotgrid"></div>
    <div class="hero-eyebrow">Compliance Intelligence Platform &nbsp;&middot;&nbsp; v1.0</div>
    <div class="hero-title">AI Banking Compliance Auditor<span class="cursor-blink"></span></div>
    <p class="hero-sub">
        Screen banking documents and transactions for AML/KYC and credit risk.<br>
        Powered by a rule engine, Markov credit modelling, and Google Gemini.
    </p>
    <div class="badge-row">
        <span class="badge b-teal">AML / KYC</span>
        <span class="badge b-teal">Basel III/IV</span>
        <span class="badge b-blue">MiFID II</span>
        <span class="badge b-blue">PSD2</span>
        <span class="badge b-purp">Markov Credit Model</span>
        <span class="badge b-purp">Gemini AI</span>
    </div>
</div>
"""


def render_hero() -> None:
    """Inject the hero banner HTML into the page."""
    st.markdown(_HERO_HTML, unsafe_allow_html=True)
