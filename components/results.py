"""
components/results.py -- Audit results display
ESG Provenance Auditor

Renders everything that appears after the user clicks "Run AI Audit":
  - Loading spinner
  - Report header with company name and verified chip
  - Key metrics (left column)
  - SASB compliance breakdown table (right column)
  - Blockchain verification footer with SHA-256 hash
"""

import hashlib
import time

import streamlit as st

import config


def render_results(uploaded_file, standards: list[str]) -> None:
    """Display the full audit results panel.

    Args:
        uploaded_file: The Streamlit UploadedFile from the file uploader.
        standards:     List of selected framework strings.
    """
    # ── Simulated agent processing ────────────────────────────────
    with st.spinner(
        "Agent analyzing PDF structure\u2026 extracting ESG metrics\u2026 "
        "verifying SASB compliance\u2026"
    ):
        time.sleep(3)

    company = (
        uploaded_file.name.rsplit(".", 1)[0]
        .replace("_", " ")
        .replace("-", " ")
        .upper()
    )

    # ── Report header ─────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="results">
        <div class="report-bar">
            <div>
                <span class="slabel" style="margin-bottom:.18rem;">Audit Report</span>
                <div style="font-family:var(--f-display);font-size:1.35rem;font-weight:700;
                            color:var(--text-hi);letter-spacing:-.022em;">{company}</div>
            </div>
            <span class="verified-chip">\u2713 Verified</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m_col, d_col = st.columns([1, 2], gap="large")

    # ── Left column: key metrics ──────────────────────────────────
    with m_col:
        st.markdown(
            '<span class="slabel">Key Metrics</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="metric-card stagger-1">
                <div class="mc-label">Overall Compliance Score</div>
                <div class="mc-value">82%</div>
                <div class="mc-delta mc-delta--pos">\u25b2 Highly Compliant</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="metric-card stagger-2" style="margin-top:0.75rem;">
                <div class="mc-label">Data Transparency Rating</div>
                <div class="mc-value">A\u2212</div>
                <div class="mc-delta mc-delta--pos">\u25b2 High</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="metric-card stagger-3" style="margin-top:0.75rem;">
                <div class="mc-label">Flagged Issues</div>
                <div class="mc-value">2</div>
                <div class="mc-delta mc-delta--pos">\u2193 \u22121 vs Last Year</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Applied-standards card
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

    # ── Right column: SASB compliance table ───────────────────────
    with d_col:
        st.markdown(
            '<span class="slabel">SASB Compliance Breakdown</span>',
            unsafe_allow_html=True,
        )

        rows_html = ""
        for i, (crit, status, excerpt) in enumerate(config.SASB_ROWS):
            stripe = "background:rgba(255,255,255,0.013);" if i % 2 == 0 else ""
            badge = config.STATUS_BADGES[status]
            rows_html += (
                f'<tr style="{stripe}">'
                f"<td>{crit}</td>"
                f'<td style="text-align:center;">{badge}</td>'
                f"<td>{excerpt}</td>"
                f"</tr>"
            )

        st.markdown(
            f"""
            <div class="stagger-4">
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
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Blockchain verification footer ────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    audit_hash = hashlib.sha256(uploaded_file.name.encode()).hexdigest()
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
                    <span class="slabel" style="margin-bottom:.3rem;">Audit Hash (SHA-256)</span>
                    <div class="hash-val">{audit_hash}</div>
                    <div class="chain-status">
                        Status: <strong>Anchored to Silent Data (Applied Blockchain L2)</strong>
                    </div>
                    <div class="chain-sub">Standards applied: {stds_joined}</div>
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
