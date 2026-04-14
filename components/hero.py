"""
components/hero.py -- Hero banner section
ESG Provenance Auditor

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
    <div class="hero-eyebrow">ESG Intelligence Platform &nbsp;&middot;&nbsp; v1.0</div>
    <div class="hero-title">AI Banking Compliance Auditor<span class="cursor-blink"></span></div>
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
"""


def render_hero() -> None:
    """Inject the hero banner HTML into the page."""
    st.markdown(_HERO_HTML, unsafe_allow_html=True)
