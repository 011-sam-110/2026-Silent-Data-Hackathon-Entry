"""
components/input_zone.py -- File upload & framework selector
ESG Provenance Auditor

Renders the input area that visually merges with the hero card above:
  - Left column:  PDF file uploader
  - Right column: audit framework multiselect
  - Center:       "Run AI Audit" action button

Also injects the JS that applies the .esg-input-zone class to the
Streamlit container so the card border is continuous.
"""

import streamlit as st

import config
from helpers import load_js


def render_input_zone() -> tuple:
    """Render the input controls and return user selections.

    Returns:
        (uploaded_file, standards, run_audit) -- the UploadedFile
        (or None), list of selected framework strings, and bool
        indicating whether the audit button was clicked.
    """
    # Inject the DOM manipulation script that merges hero + input zone.
    load_js("scripts/input_zone.js")

    # ── Two-column layout: uploader | framework selector ──────────
    col_up, col_std = st.columns([1, 1], gap="medium")

    with col_up:
        st.markdown(
            '<span class="slabel">Sustainability Report</span>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type="pdf",
            label_visibility="collapsed",
        )

    with col_std:
        st.markdown(
            '<span class="slabel">Audit Framework</span>',
            unsafe_allow_html=True,
        )
        standards = st.multiselect(
            "Standards",
            config.FRAMEWORK_OPTIONS,
            default=config.DEFAULT_FRAMEWORK,
            label_visibility="collapsed",
        )

    # ── Centred action button ─────────────────────────────────────
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        run_audit = st.button(
            "\u26a1 Run AI Audit", type="primary", use_container_width=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    return uploaded_file, standards, run_audit
