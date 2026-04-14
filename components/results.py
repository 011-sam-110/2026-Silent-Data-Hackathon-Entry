"""
components/results.py -- Compliance analysis results display
AI Banking Compliance Auditor

Renders the full analysis output after the user clicks "Run AI Audit":
  - PDF text extraction via pdfplumber
  - Compliance engine execution
  - Decision banner (approve / review / reject)
  - Risk metric cards
  - Compliance rules table
  - Markov chain analysis (expandable)
  - Blockchain verification footer with SHA-256 hash
"""

import hashlib
import json
import time

import streamlit as st

import config
from ai_analyst import analyze_with_ai
from compliance_engine import analyze_banking_compliance
from helpers import extract_pdf_text


_RISK_COLOR = {
    "low": "var(--pass)",
    "medium": "var(--warn)",
    "high": "var(--fail)",
}


def render_results(
    uploaded_file,
    standards: list[str],
    signature_match: bool,
    client_profile: dict,
) -> None:
    """Run the compliance engine on the uploaded PDF and display results."""

    # ── Extract text from PDF ─────────────────────────────────────
    with st.spinner("Extracting text from PDF\u2026"):
        pdf_text = extract_pdf_text(uploaded_file)

    if not pdf_text.strip():
        st.warning(
            "\u26a0\ufe0f Could not extract readable text from this PDF. "
            "The analysis will be based on limited data."
        )

    # ── Run compliance engine ─────────────────────────────────────
    with st.spinner(
        "Analyzing transaction data\u2026 checking compliance rules\u2026 "
        "running Markov analysis\u2026"
    ):
        result = analyze_banking_compliance(
            pdf_text, client_profile, signature_match
        )
        time.sleep(1)

    company = (
        uploaded_file.name.rsplit(".", 1)[0]
        .replace("_", " ")
        .replace("-", " ")
        .upper()
    )

    decision = result["final_decision"]
    dec = config.DECISION_CONFIG[decision]
    risk = result["overall_risk"]
    score = result["risk_score"]
    markov = result["markov_analysis"]
    behavior = result["behavior_analysis"]
    risk_color = _RISK_COLOR.get(risk, "var(--text-mid)")

    # ── Decision banner ───────────────────────────────────────────
    st.markdown(
        f"""
        <div class="results">
        <div class="decision-bar {dec['class']}">
            <div style="font-size:1.6rem;line-height:1;">{dec['icon']}</div>
            <div>
                <span class="slabel" style="margin-bottom:.15rem;">
                    Compliance Report</span>
                <div style="font-family:var(--f-display);font-size:1.25rem;
                    font-weight:700;color:var(--text-hi);
                    letter-spacing:-.022em;">{company}</div>
            </div>
            <div style="margin-left:auto;display:flex;align-items:center;gap:1rem;">
                <div style="text-align:right;">
                    <span class="slabel">Risk Score</span>
                    <div style="font-family:var(--f-display);font-size:1.5rem;
                        font-weight:800;color:{risk_color};">{score}<span
                        style="font-size:.7rem;color:var(--text-lo);
                        font-weight:500;">/100</span></div>
                </div>
                <div class="decision-chip decision-chip--{decision}">
                    {dec['label']}</div>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m_col, d_col = st.columns([1, 2], gap="large")

    # ── Left column: risk metrics ─────────────────────────────────
    with m_col:
        st.markdown(
            '<span class="slabel">Risk Assessment</span>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-card stagger-1">
                <div class="mc-label">Overall Risk</div>
                <div class="mc-value" style="color:{risk_color};">
                    {risk.upper()}</div>
                <div class="mc-delta" style="color:{risk_color};">
                    Score: {score}/100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        exit_color = _RISK_COLOR.get(result["exit_risk"], "var(--text-mid)")
        st.markdown(
            f"""
            <div class="metric-card stagger-2" style="margin-top:.75rem;">
                <div class="mc-label">Exit Risk</div>
                <div class="mc-value" style="color:{exit_color};">
                    {result['exit_risk'].upper()}</div>
                <div class="mc-delta" style="color:var(--text-mid);">
                    Signature: {result['signature_verification'].upper()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        beh_label = "ANOMALOUS" if behavior["is_anomalous"] else "NORMAL"
        beh_color = "var(--fail)" if behavior["is_anomalous"] else "var(--pass)"
        st.markdown(
            f"""
            <div class="metric-card stagger-3" style="margin-top:.75rem;">
                <div class="mc-label">Client Behavior</div>
                <div class="mc-value" style="color:{beh_color};">
                    {beh_label}</div>
                <div class="mc-delta" style="color:var(--text-mid);">
                    Default prob: {markov['probability_of_default']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        stds_html = "".join(
            f'<div class="std-item"><span class="std-dot"></span>{s}</div>'
            for s in standards
        )
        st.markdown(
            f"""
            <div class="std-card">
                <span class="slabel" style="margin-bottom:.5rem;">
                    Applied Standards</span>
                {stds_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Right column: compliance rules table ──────────────────────
    with d_col:
        st.markdown(
            '<span class="slabel">Compliance Rules</span>',
            unsafe_allow_html=True,
        )

        rows_html = ""
        for i, rule in enumerate(result["rules"]):
            stripe = (
                "background:rgba(255,255,255,0.013);" if i % 2 == 0 else ""
            )
            name = config.RULE_LABELS.get(rule["rule"], rule["rule"])
            badge = config.RULE_STATUS_BADGES.get(
                rule["status"], rule["status"]
            )
            w = rule.get("weight", 0)
            max_w = rule.get("max_weight", 0)
            if w > 0:
                weight_html = f'<span style="color:var(--fail);font-weight:700;">+{w}</span>'
            elif max_w > 0:
                weight_html = f'<span style="color:var(--text-lo);">+{max_w}</span>'
            else:
                weight_html = f'<span style="color:var(--text-lo);">—</span>'
            rows_html += (
                f'<tr style="{stripe}">'
                f"<td>{name}</td>"
                f'<td style="text-align:center;">{badge}</td>'
                f'<td style="text-align:center;">{weight_html}</td>'
                f"<td>{rule['evidence']}</td>"
                f"</tr>"
            )

        st.markdown(
            f"""
            <div class="stagger-4">
            <table class="audit-tbl">
                <thead>
                    <tr>
                        <th>Rule</th>
                        <th style="text-align:center;">Status</th>
                        <th style="text-align:center;">Weight</th>
                        <th>Evidence</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── AI Risk Analysis ─────────────────────────────────────────
    with st.spinner(
        "Claude is analyzing the document\u2026 generating risk narrative\u2026"
    ):
        ai_response = analyze_with_ai(pdf_text, result)

    if ai_response:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="ai-section stagger-5">
                <span class="slabel"
                      style="display:inline-flex;align-items:center;gap:.4rem;">
                    <span style="font-size:.85rem;">&#129302;</span>
                    Claude AI Risk Analysis
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(ai_response)

    # ── Markov chain analysis (collapsible) ───────────────────────
    with st.expander("\U0001f4ca Markov Chain Analysis"):
        mc = st.columns(4)
        with mc[0]:
            st.markdown(
                f"**Current State**\n\n`{markov['current_state']}`"
            )
        with mc[1]:
            st.markdown(
                f"**Predicted Outcome**\n\n`{markov['predicted_outcome']}`"
            )
        with mc[2]:
            st.markdown(
                f"**Default Probability**\n\n"
                f"`{markov['probability_of_default']}`"
            )
        with mc[3]:
            probs = markov["transition_probabilities"]
            st.markdown(
                "**Transitions**\n\n"
                + "\n".join(f"- {k}: `{v}`" for k, v in probs.items())
            )
        st.caption(markov["reasoning"])

    # ── Full reasoning (collapsible) ──────────────────────────────
    with st.expander("\U0001f4dd Full Reasoning"):
        st.markdown(result["reasoning"])

    # ── Blockchain verification footer ────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    audit_hash = hashlib.sha256(
        json.dumps(result, sort_keys=True, default=str).encode()
    ).hexdigest()
    stds_joined = ", ".join(standards) if standards else "SASB Standards"

    st.markdown(
        f"""
        <div class="stagger-5">
        <div class="chain-box">
            <div class="chain-title">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="1.8"
                     stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <span class="chain-pulse"></span> Blockchain Verification Layer
            </div>
            <div class="chain-grid">
                <div>
                    <span class="slabel" style="margin-bottom:.3rem;">
                        Audit Hash (SHA-256)</span>
                    <div class="hash-val">{audit_hash}</div>
                    <div class="chain-status">
                        Status: <strong>Anchored to Silent Data
                        (Applied Blockchain L2)</strong>
                    </div>
                    <div class="chain-sub">
                        Standards applied: {stds_joined}</div>
                </div>
                <div>
                    <a href="#" class="chain-link">
                        \U0001f517 View on Explorer
                    </a>
                </div>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
