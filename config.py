"""
config.py -- Application constants and mock data
AI Banking Compliance Auditor

Pure data module with no Streamlit imports. Houses page configuration,
framework options, and the hardcoded audit rows used in the demo.
"""

# -----------------------------------------------------------------------
# PAGE CONFIG
# Passed as kwargs to st.set_page_config(). Must be the first Streamlit
# call in the app entry point.
# -----------------------------------------------------------------------
PAGE_CONFIG = dict(
    page_title="AI Banking Compliance Auditor",
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
    "AML / KYC",
    "Basel III / IV",
    "MiFID II",
    "PSD2",
    "High-risk country watchlist",
]
DEFAULT_FRAMEWORK = ["AML / KYC"]

# -----------------------------------------------------------------------
# COMPLIANCE ENGINE -- display config
# Human-readable rule labels and status badge HTML.
# -----------------------------------------------------------------------
RULE_LABELS = {
    "high_transaction_amount": "High Transaction Amount",
    "unknown_or_new_recipient": "Unknown / New Recipient",
    "high_risk_country": "High-Risk Country",
    "medium_risk_country": "Medium-Risk Country",
    "vague_or_missing_details": "Vague / Missing Details",
    "urgency_or_pressure_language": "Urgency Language",
    "signature_verification": "Signature Verification",
    "behavior_amount_vs_average": "Amount vs Average",
    "behavior_typical_countries": "Typical Countries",
    "behavior_usual_recipients": "Usual Recipients",
}

RULE_STATUS_BADGES = {
    "pass": '<span class="sp sp-p">\u2705 PASS</span>',
    "fail": '<span class="sp sp-f">\u274c FAIL</span>',
}

DECISION_CONFIG = {
    "approve": {"icon": "\u2705", "label": "APPROVE", "class": "decision-approve"},
    "review":  {"icon": "\u26a0\ufe0f", "label": "REVIEW",  "class": "decision-review"},
    "reject":  {"icon": "\u274c", "label": "REJECT",  "class": "decision-reject"},
}
