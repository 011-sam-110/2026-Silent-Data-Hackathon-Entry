"""
components -- UI building blocks
ESG Provenance Auditor

Re-exports the three top-level render functions so callers can write:
    from components import render_hero, render_input_zone, render_results
"""

from components.hero import render_hero
from components.input_zone import render_input_zone
from components.results import render_results

__all__ = ["render_hero", "render_input_zone", "render_results"]
