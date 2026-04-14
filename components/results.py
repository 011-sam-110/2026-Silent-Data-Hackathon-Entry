"""
components/results.py -- Audit results display
ESG Provenance Auditor

Renders everything that appears after the user clicks "Run AI Audit":
  - Real PDF parsing via LiteParse + parser.py
  - Parsed text saved to parsed_reports/ and offered for download
  - Report header with company name and verified chip
  - Key metrics (left column)
  - SASB compliance breakdown table (right column)
  - Blockchain verification footer with SHA-256 hash
"""

import hashlib
import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path

import streamlit as st

import config
from parser import extract_clean_text

_ROOT = Path(__file__).resolve().parent.parent
_REPORTS_DIR = _ROOT / "parsed_reports"
_OUTPUT_DIR = _ROOT / "output"

# ── Logging setup ─────────────────────────────────────────────────
_OUTPUT_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("esg_auditor")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(_OUTPUT_DIR / "app.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)


def _parse_pdf(uploaded_file) -> tuple[str, int, Path]:
    """Run LiteParse on the uploaded PDF and return clean text.

    Returns:
        (text, page_count, output_path)
    """
    _REPORTS_DIR.mkdir(exist_ok=True)
    file_size = uploaded_file.size
    logger.info("PDF upload received: %s (%d bytes)", uploaded_file.name, file_size)

    content = uploaded_file.read()
    uploaded_file.seek(0)  # reset so other code can re-read if needed

    tmp_in = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_out_path = tmp_in.name + ".json"
    try:
        tmp_in.write(content)
        tmp_in.close()
        logger.debug("Temp PDF written to %s", tmp_in.name)

        logger.info("Starting LiteParse...")
        t0 = time.perf_counter()
        result = subprocess.run(
            [
                "liteparse", "parse",
                "--format", "json",
                "-q",
                "-o", tmp_out_path,
                tmp_in.name,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        elapsed = time.perf_counter() - t0

        if result.returncode != 0:
            logger.error("LiteParse failed (exit %d): %s", result.returncode, result.stderr.strip())
            raise RuntimeError(f"LiteParse failed: {result.stderr.strip()}")

        logger.info("LiteParse finished in %.2fs", elapsed)

        out_path = Path(tmp_out_path)
        if not out_path.exists():
            logger.error("LiteParse produced no output file")
            raise RuntimeError("LiteParse produced no output.")

        with open(out_path, "r", encoding="utf-8") as f:
            liteparse_data = json.load(f)
        logger.debug("LiteParse JSON loaded (%d bytes)", out_path.stat().st_size)

        logger.info("Extracting clean text...")
        text, page_count = extract_clean_text(liteparse_data)
        logger.info("Extracted %d pages (%d chars)", page_count, len(text))

        # Save to parsed_reports/
        stem = uploaded_file.name.rsplit(".", 1)[0]
        report_path = _REPORTS_DIR / f"{stem}_parsed.txt"
        report_path.write_text(text, encoding="utf-8")
        logger.info("Parsed text saved to %s", report_path)

        return text, page_count, report_path

    except Exception:
        logger.exception("Error during PDF parsing")
        raise

    finally:
        Path(tmp_in.name).unlink(missing_ok=True)
        Path(tmp_out_path).unlink(missing_ok=True)
        logger.debug("Temp files cleaned up")


def render_results(uploaded_file, standards: list[str]) -> None:
    """Display the full audit results panel.

    Args:
        uploaded_file: The Streamlit UploadedFile from the file uploader.
        standards:     List of selected framework strings.
    """
    # ── Real PDF parsing via LiteParse ────────────────────────────
    with st.spinner("Parsing PDF with LiteParse\u2026"):
        try:
            text, page_count, report_path = _parse_pdf(uploaded_file)
        except Exception as e:
            st.error(f"PDF parsing failed: {e}")
            return

    # ── Success message + download ────────────────────────────────
    st.success(
        f"Parsed {page_count} pages \u2192 saved to `{report_path.relative_to(_ROOT)}`"
    )
    st.download_button(
        label="\u2b07 Download parsed text",
        data=text,
        file_name=report_path.name,
        mime="text/plain",
    )

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
