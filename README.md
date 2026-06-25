<p align="center">
  <img src="https://github.com/user-attachments/assets/9067b182-157f-487d-a96a-33e5ac50d758" width="640" alt="AI Banking Compliance Auditor">
</p>

<h1 align="center">AI Banking Compliance Auditor</h1>
<p align="center">Upload a banking document and get an AML/KYC risk verdict from a rule engine, a Markov credit model, and Gemini.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white">
  <img src="https://img.shields.io/badge/AI-Gemini%202.0%20Flash-4285F4?logo=google&logoColor=white">
</p>

A real-time compliance analysis demo built at the **Silent Data Hackathon** by a team of three
(Sam, [ili-spec](https://github.com/ili-spec), [LBSiUK](https://github.com/LBSiUK)). Upload a PDF
(wire-transfer memo, payment instruction, annual/sustainability report) and it returns an
**Approve / Manual Review / Reject** verdict from three stacked layers, alongside a SHA-256 hash of
the result as a tamper-evident fingerprint.

## ✨ Features
- **PDF ingestion** — extracts and normalises text with `pdfplumber`.
- **Rule-based compliance engine** — 10 weighted AML/KYC rules (0–100 score): high-risk-country watchlist (keyword-matched, not a live OFAC/SDN feed), urgency/pressure language, signature verification, behavioural anomaly scoring, exit-fraud classification.
- **Markov credit model** — builds a transition matrix from the detected risk signals and projects 3-step default probability across four states (GOOD → NORMAL → RISKY → DEFAULT).
- **Gemini risk narrative** — sends document text + engine results to Gemini 2.0 Flash for an expert write-up framed against Basel III/IV, MiFID II, PSD2, and ESG greenwashing risk.
- **Tamper-evident hash** — every result is SHA-256 hashed so any change to the verdict is detectable.
- **Dark fintech UI** — a custom layered CSS design system (tokens / shell / hero / forms / results) with an animated video background, all inside Streamlit.

## 🛠 Stack
Python 3.10+ · Streamlit + custom CSS/JS · Google Gemini 2.0 Flash (`google-generativeai`) · pdfplumber · SHA-256 result hashing.

## 🚀 Run
```bash
git clone https://github.com/011-sam-110/2026-Silent-Data-Hackathon-Entry
cd 2026-Silent-Data-Hackathon-Entry
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key_here" > .env
streamlit run app.py
```
The AI narrative activates only when a key is present; the rule engine and Markov model run without
it. Sample PDFs (HIGH / MEDIUM / LOW risk) are in `test_data/`.

## 🧠 How it works
A layered pipeline: ingestion → rule engine → AI analyst → verification.

| Layer | What it does |
|---|---|
| **Compliance rule engine** (`compliance_engine.py`) | 10 AML/KYC/sanctions rules → weighted 0–100 risk score |
| **Markov credit model** (`compliance_engine.py`) | 3-step default probability over four credit states |
| **Gemini analyst** (`ai_analyst.py`) | risk narrative, flags the rules may miss, recommendations |

`app.py` wires config, assets and the Streamlit components (`components/hero.py`, `input_zone.py`,
`results.py`); styling lives in `styles/`.

## 🗺 Roadmap
Working hackathon build; runs locally.
- [ ] On-chain anchoring of the result hash to Silent Data (Applied Blockchain L2) — designed for, not yet implemented; the current build hashes locally
- Known limitation: high-risk-country screening is a built-in keyword watchlist, not a live OFAC/SDN feed
- Known limitation: a hackathon demo for screening assistance, not a certified compliance system
