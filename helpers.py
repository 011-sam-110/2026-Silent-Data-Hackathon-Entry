"""
helpers.py -- Asset-loading utilities
ESG Provenance Auditor

Provides load_css() and load_js() for injecting external CSS and JS
files into the Streamlit page. All paths are resolved relative to
this file's parent directory so the app works regardless of the
working directory used to launch Streamlit.
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# Anchor all relative paths to the project root (where this file lives).
_ROOT = Path(__file__).parent


def load_css(*css_files: str) -> None:
    """Read one or more CSS files and inject them as a single <style> tag.

    Files are concatenated in the order given. Put tokens.css first so
    :root custom properties are defined before any other selector
    references them via var(--name).
    """
    parts: list[str] = []
    for relpath in css_files:
        parts.append((_ROOT / relpath).read_text(encoding="utf-8"))
    st.markdown(f"<style>{''.join(parts)}</style>", unsafe_allow_html=True)


def load_js(js_file: str, *, height: int = 0) -> None:
    """Read a JS file and inject it via components.html().

    Each call creates its own iframe — this is how Streamlit's
    components.html works. The JS inside can access the parent page
    through window.parent.document.
    """
    code = (_ROOT / js_file).read_text(encoding="utf-8")
    components.html(f"<script>{code}</script>", height=height, scrolling=False)
