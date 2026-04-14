"""
ai_analyst.py -- Gemini AI integration for banking compliance analysis

Sends extracted PDF text and compliance engine results to Google Gemini for
deep analysis. Returns a markdown-formatted risk narrative with additional
flags and recommendations that the rule engine may miss.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import google.generativeai as genai

_ROOT = Path(__file__).parent

_SYSTEM_PROMPT = (
    "You are a senior banking compliance analyst with deep expertise in "
    "AML, KYC, sanctions screening, fraud detection, and regulatory "
    "compliance (Basel III/IV, MiFID II, PSD2). You have been given "
    "the extracted text from a document and the results of an automated "
    "compliance rule engine.\n\n"
    "Provide your analysis in three clearly marked sections:\n\n"
    "## Risk Narrative\n"
    "A concise (2-3 paragraph) analysis of the document content, "
    "referencing specific amounts, entities, countries, dates, and "
    "page numbers where found.\n\n"
    "## Additional Flags\n"
    "Bullet list of risks, red flags, or concerns the automated engine "
    "may have missed. If none, say so explicitly.\n\n"
    "## Recommendations\n"
    "Bullet list of actionable next steps for the compliance team.\n\n"
    "Be specific, professional, and evidence-based. If the document is "
    "a corporate/annual report, also assess ESG disclosures, "
    "greenwashing risk, and reporting gaps."
)


def _load_api_key() -> str | None:
    """Read the Gemini API key from .env."""
    env_path = _ROOT / ".env"
    if not env_path.exists():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("GEMINI_API_KEY="):
            return line[len("GEMINI_API_KEY="):]
    return None


def analyze_with_ai(
    pdf_text: str,
    engine_results: dict[str, Any],
) -> str | None:
    """Send PDF text and engine results to Gemini for deep analysis.

    Returns a markdown string with the AI analysis, or an error message.
    Returns None if no API key is configured.
    """
    api_key = _load_api_key()
    if not api_key:
        return None

    rules_summary = "\n".join(
        f"- **{r['rule']}**: {r['status'].upper()} \u2014 {r['evidence']}"
        for r in engine_results.get("rules", [])
    )

    markov = engine_results.get("markov_analysis", {})
    behavior = engine_results.get("behavior_analysis", {})

    user_msg = (
        f"{_SYSTEM_PROMPT}\n\n"
        "## Document Text (extracted from PDF)\n"
        f"{pdf_text[:15000]}\n\n"
        "## Automated Compliance Engine Results\n"
        f"- **Risk Score:** {engine_results.get('risk_score', 'N/A')}/100\n"
        f"- **Final Decision:** {engine_results.get('final_decision', 'N/A').upper()}\n"
        f"- **Overall Risk:** {engine_results.get('overall_risk', 'N/A').upper()}\n"
        f"- **Exit Risk:** {engine_results.get('exit_risk', 'N/A')}\n"
        f"- **Signature Verification:** "
        f"{engine_results.get('signature_verification', 'N/A')}\n"
        f"- **Behavior:** {behavior.get('details', 'N/A')}\n"
        f"- **Default Probability:** "
        f"{markov.get('probability_of_default', 'N/A')}\n"
        f"- **Predicted Outcome:** "
        f"{markov.get('predicted_outcome', 'N/A')}\n\n"
        "### Rule Results\n"
        f"{rules_summary}\n\n"
        "### Engine Reasoning\n"
        f"{engine_results.get('reasoning', 'N/A')}\n\n"
        "Provide your analysis now."
    )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(user_msg)
        return response.text
    except Exception as exc:
        return f"**AI analysis unavailable:** {exc}"
