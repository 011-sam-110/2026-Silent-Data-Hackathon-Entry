"""
config.py -- Application constants and mock data
ESG Provenance Auditor

Pure data module with no Streamlit imports. Houses page configuration,
framework options, and the hardcoded audit rows used in the demo.
"""

# -----------------------------------------------------------------------
# PAGE CONFIG
# Passed as kwargs to st.set_page_config(). Must be the first Streamlit
# call in the app entry point.
# -----------------------------------------------------------------------
PAGE_CONFIG = dict(
    page_title="ESG Provenance Auditor",
    page_icon="\U0001f6e1\ufe0f",          # shield emoji
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------
# VIDEO PATHS
# Streamlit serves ./static/ at /app/static/ when enableStaticServing
# is true in .streamlit/config.toml. A hard-link avoids duplicating
# the large video file on the same volume.
# -----------------------------------------------------------------------
VIDEO_SRC = "media/14003675-uhd_3840_2160_60fps.mp4"
VIDEO_DST = "static/bg-video.mp4"

# -----------------------------------------------------------------------
# AUDIT FRAMEWORK OPTIONS
# Choices shown in the multiselect widget.
# -----------------------------------------------------------------------
FRAMEWORK_OPTIONS = [
    "UN Sustainable Development Goals (SDGs)",
    "SASB Standards",
    "TCFD Recommendations",
    "GRI Standards",
    "Custom 'Green Token' Criteria",
]
DEFAULT_FRAMEWORK = ["SASB Standards"]

# -----------------------------------------------------------------------
# MOCK AUDIT RESULTS
# Each row: (criteria name, status, AI evidence excerpt).
# Status must be one of the keys in STATUS_BADGES below.
# -----------------------------------------------------------------------
SASB_ROWS = [
    (
        "GHG Emissions (Scope 1 & 2)",
        "PASS",
        "'Total Scope 1 emissions reduced by 4%\u2026' (p.\u00a012)",
    ),
    (
        "Supply Chain Disclosure (Scope 3)",
        "PASS",
        "'\u2026company disclosed comprehensive Scope 3 data\u2026' (p.\u00a015)",
    ),
    (
        "Water Management Protocols",
        "PARTIAL",
        "'Water risk assessments conducted, targets unclear\u2026' (p.\u00a022)",
    ),
    (
        "Renewable Energy Target (2030)",
        "FAIL",
        "No specific 2030 renewable energy target found in text.",
    ),
    (
        "Labor Practices Disclosure",
        "PASS",
        "'\u2026all Tier 1 suppliers audited for labor compliance\u2026' (p.\u00a030)",
    ),
]

STATUS_BADGES = {
    "PASS":    '<span class="sp sp-p">\u2705 PASS</span>',
    "PARTIAL": '<span class="sp sp-w">\u26a0\ufe0f PARTIAL</span>',
    "FAIL":    '<span class="sp sp-f">\u274c FAIL</span>',
}
