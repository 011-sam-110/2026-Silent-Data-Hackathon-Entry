# AI Banking Compliance Auditor
<img width="1920" height="3517" alt="screencapture-localhost-8501-2026-04-23-00_26_40" src="https://github.com/user-attachments/assets/9067b182-157f-487d-a96a-33e5ac50d758" />
An intelligent, real-time compliance analysis platform built for the **Silent Data Hackathon**. Upload any banking document or transaction report and receive an instant, AI-powered risk verdict — powered by a custom rule engine, Markov chain credit modelling, and Google Gemini.

> **Hackathon project** — built collaboratively by a team of three developers under time pressure and shipped end-to-end in a single event.

---

## What it does

The auditor accepts a PDF (wire transfer memo, payment instruction, annual/sustainability report) and runs it through three layers of analysis:

| Layer | What it does |
|---|---|
| **Compliance rule engine** | Checks 10 AML/KYC/sanctions rules and computes a weighted risk score (0–100) |
| **Markov credit model** | Estimates 3-step default probability across four credit states (GOOD → NORMAL → RISKY → DEFAULT) |
| **Gemini AI analyst** | Generates a professional risk narrative — flags the engine may miss, plus actionable recommendations |

The final verdict is one of three decisions: **Approve**, **Manual Review**, or **Reject**, displayed alongside a SHA-256 integrity hash of the full result — a tamper-evident fingerprint of each audit.

---

## Key features

- **PDF ingestion** — extracts and normalises raw text with `pdfplumber`
- **Rule-based compliance engine** — evaluates AML rules, a high-risk-country watchlist (keyword-matched, not a live OFAC/SDN feed), urgency/pressure language detection, signature verification, behavioural anomaly scoring, and exit-fraud classification
- **Markov chain default modelling** — dynamically builds a transition matrix from detected risk signals and projects default probability over a 3-step horizon
- **Gemini 2.0 Flash integration** — sends document text + engine results to Google Gemini for an expert-level risk narrative covering Basel III/IV, MiFID II, PSD2, and ESG greenwashing risk
- **Tamper-evident result hash** — every result is SHA-256 hashed so any change to the verdict is detectable. On-chain anchoring to Silent Data (Applied Blockchain L2) is the intended next step — not yet implemented; the current build computes the hash locally
- **Dark fintech UI** — custom CSS design system (tokens, shell, hero, forms, results, verification panel) with animated video background and staggered card animations, all within Streamlit

---

## Skills demonstrated

- **Python** — clean module separation, type-annotated functions, compiled regex patterns, Markov matrix maths
- **Streamlit** — custom component architecture, raw HTML/CSS injection, multi-column layout, dynamic state management
- **LLM integration** — structured prompt engineering with Google Gemini (`google-generativeai`), context window management, fallback handling
- **Financial domain knowledge** — AML/KYC rule logic, high-risk-country screening heuristics, Basel III/IV and MiFID II regulatory framing, exit-fraud detection patterns
- **Probabilistic modelling** — Markov chain state machine with dynamically weighted transition matrices
- **UI/UX** — design token system, CSS custom properties, staggered animations, fintech-grade dark theme
- **System design** — layered architecture (ingestion → rule engine → AI analyst → verification), clean public API surface on the compliance engine

---

## Tech stack

| | |
|---|---|
| **Language** | Python 3.10+ |
| **Frontend** | Streamlit + custom CSS/JS |
| **AI** | Google Gemini 2.0 Flash (`google-generativeai`) |
| **PDF parsing** | pdfplumber |
| **Verification** | SHA-256 result hashing (on-chain anchoring planned, not yet implemented) |

---

## Getting started

```bash
git clone https://github.com/011-sam-110/collab_silent_data
cd collab_silent_data

pip install -r requirements.txt

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

streamlit run app.py
```

The AI analysis section activates only when a key is present. The rule engine and Markov model run without it.

---

## Project structure

```
├── app.py                  # Entry point — wires config, assets, and components
├── compliance_engine.py    # Rule engine + Markov chain credit model
├── ai_analyst.py           # Gemini integration and prompt engineering
├── config.py               # Constants, page config, decision config
├── helpers.py              # CSS/JS loaders, PDF text extraction
├── components/
│   ├── hero.py             # Hero banner
│   ├── input_zone.py       # File upload, framework selector, client profile
│   └── results.py          # Full results render — metrics, rules table, AI output, blockchain footer
└── styles/                 # Layered CSS design system
```

---

## Team

Built by three developers during the **Silent Data Hackathon**:

- **[011-sam-110](https://github.com/011-sam-110)** (Sam)
- **[ili-spec](https://github.com/ili-spec)**
- **[LBSiUK](https://github.com/LBSiUK)**

---

## Regulatory coverage

The compliance engine and AI analyst prompt are scoped to:

- Anti-Money Laundering (AML) & Know Your Customer (KYC)
- High-risk country flagging (built-in keyword watchlist; not a live OFAC/SDN feed)
- Basel III / Basel IV capital and risk frameworks
- MiFID II (Markets in Financial Instruments Directive)
- PSD2 (Payment Services Directive)
- ESG disclosure integrity and greenwashing risk
