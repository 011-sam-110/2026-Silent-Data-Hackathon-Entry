"""Banking Compliance Engine — Python port.

This module provides a rule-based banking compliance analysis engine that
evaluates wire-transfer and payment transaction text against a configurable
set of anti-money-laundering (AML) and fraud-detection heuristics.  It checks
for high-risk countries, unusual amounts, new or unknown recipients, urgency
language, vague transaction details, signature verification, and behavioral
anomalies relative to a client profile.  A Markov-chain credit-state model
estimates the probability of default over a short horizon.  The single public
entry point, ``analyze_banking_compliance``, returns a structured dict with
per-rule results, an aggregate risk score, a final decision
(approve / review / reject), and the full Markov analysis.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

HIGH_RISK_COUNTRIES: tuple[str, ...] = (
    "iran",
    "north korea",
    "syria",
    "afghanistan",
    "myanmar",
    "russia",
    "belarus",
    "yemen",
    "somalia",
    "venezuela",
)

MEDIUM_RISK_COUNTRIES: tuple[str, ...] = (
    "algeria",
    "angola",
    "cameroon",
    "cote d'ivoire",
    "ivory coast",
    "kenya",
    "lebanon",
    "namibia",
    "south sudan",
    "syria",
    "yemen",
    "bolivia",
    "haiti",
    "venezuela",
    "bulgaria",
    "monaco",
    "kuwait",
    "lao pdr",
    "nepal",
    "papua new guinea",
    "vietnam",
)

URGENCY_TERMS: tuple[str, ...] = (
    "urgent",
    "urgently",
    "asap",
    "immediately",
    "without delay",
    "today",
    "right now",
    "rush",
    "time sensitive",
    "must be sent now",
    "act now",
    "execute immediately",
    "accelerate rollout",
    "rapid deployment",
    "fast-track",
    "instant implementation",
    "swift execution",
    "expedited timeline",
    "urgent mandate",
    "priority one",
    "capture momentum",
    "seize the window",
    "market-first advantage",
    "competitive necessity",
    "time-sensitive entry",
    "outpace rivals",
    "first-mover urgency",
    "defend share",
    "closing gap",
    "critical inflection",
    "mitigate exposure",
    "avert risk",
    "time-critical hedge",
    "de-risk now",
    "proactive defense",
    "stop-loss action",
    "volatility protection",
    "stabilize immediately",
    "resilience priority",
    "risk-off mandate",
    "maximize returns",
    "unlock value",
    "scale instantly",
    "immediate upside",
    "growth catalyst",
    "strategic sprint",
    "aggressive expansion",
    "capitalize today",
    "high-velocity growth",
    "targeted strike",
    "last-call opportunity",
    "firm deadline",
    "closing window",
    "critical threshold",
    "point of impact",
    "final phase",
    "non-negotiable timeline",
    "sunset period",
    "zero-hour",
    "limited availability",
)

VAGUE_TERMS: tuple[str, ...] = (
    "misc",
    "miscellaneous",
    "other",
    "support",
    "personal",
    "project",
    "general payment",
    "business matter",
    "help",
    "services",
)

DETAIL_TERMS: tuple[str, ...] = (
    "invoice",
    "contract",
    "salary",
    "rent",
    "tuition",
    "loan repayment",
    "purchase order",
    "vendor",
    "supplier",
    "customer",
    "payment for",
)

NEW_RECIPIENT_TERMS: tuple[str, ...] = (
    "new recipient",
    "new payee",
    "new beneficiary",
    "first time recipient",
    "first time payment",
    "never paid before",
    "unknown recipient",
    "unfamiliar account",
)

STATES: list[str] = ["GOOD", "NORMAL", "RISKY", "DEFAULT"]

# ---------------------------------------------------------------------------
# Amount-detection patterns (compiled once at module level)
# ---------------------------------------------------------------------------

_AMOUNT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(?:usd|gbp|eur|\$)\s?(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?\s?"
        r"(?:usd|gbp|eur|dollars|pounds|euros)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(\d{5,})(?:\.\d{2})?\b"),
]

# ---------------------------------------------------------------------------
# Recipient-detection patterns
# ---------------------------------------------------------------------------

_RECIPIENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\bbeneficiary[:\s]+([a-z0-9&.\- ]{3,40}?)"
        r"(?=\s+(?:in|for|from|regarding)\b|$|,)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\brecipient[:\s]+([a-z0-9&.\- ]{3,40}?)"
        r"(?=\s+(?:in|for|from|regarding)\b|$|,)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bpayee[:\s]+([a-z0-9&.\- ]{3,40}?)"
        r"(?=\s+(?:in|for|from|regarding)\b|$|,)",
        re.IGNORECASE,
    ),
    # Note: the JS version uses a case-sensitive leading [A-Z] for this pattern
    re.compile(
        r"\bto\s+([A-Z][A-Za-z0-9&.\- ]{2,40}?)"
        r"(?=\s+(?:in|for|from|regarding)\b|$|,)"
    ),
]

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _normalize_list(value: Any) -> list[str]:
    """Return *value* as a list of lowered, stripped, non-empty strings."""
    if not isinstance(value, list):
        return []
    return [s for item in value if (s := str(item).strip().lower())]


def _unique_list(items: list[str]) -> list[str]:
    """De-duplicate *items* while preserving insertion order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _round_prob(value: float) -> float:
    """Clamp *value* to [0, 1] and round to four decimal places."""
    return round(max(0.0, min(1.0, value)), 4)


def _make_snippet(raw_text: str, text: str, match: str | None) -> str:
    """Return a short excerpt of *raw_text* centred on *match*."""
    if not raw_text:
        return "No transaction text provided."
    if not match:
        return raw_text[:140]
    phrase = str(match).lower()
    start_index = text.find(phrase)
    if start_index == -1:
        return raw_text[:140]
    start = max(0, start_index - 30)
    end = min(len(raw_text), start_index + len(phrase) + 40)
    return raw_text[start:end]


def _add_rule(
    rules: list[dict[str, str]], rule: str, failed: bool, evidence: str, weight: int = 0
) -> None:
    rules.append(
        {
            "rule": rule,
            "status": "fail" if failed else "pass",
            "evidence": evidence,
            "weight": weight if failed else 0,
            "max_weight": weight,
        }
    )


def _detect_amount(raw_text: str) -> dict[str, Any]:
    for pattern in _AMOUNT_PATTERNS:
        match = pattern.search(raw_text)
        if match is None:
            continue
        amount_str = str(match.group(1)).replace(",", "")
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            continue
        return {"amount": amount, "source": match.group(0)}
    return {"amount": None, "source": ""}


def _detect_country(
    text: str, profile: dict[str, Any]
) -> str | None:
    known_countries = _unique_list(
        list(HIGH_RISK_COUNTRIES)
        + list(MEDIUM_RISK_COUNTRIES)
        + _normalize_list(profile.get("typical_countries"))
        + _normalize_list(profile.get("usual_countries"))
        + [
            "uk",
            "united kingdom",
            "usa",
            "united states",
            "germany",
            "france",
            "uae",
            "dubai",
            "china",
            "india",
            "nigeria",
            "singapore",
            "switzerland",
        ]
    )
    for country in known_countries:
        if country in text:
            return country
    return None


def _detect_recipient(
    raw_text: str, text: str, profile: dict[str, Any]
) -> str | None:
    for pattern in _RECIPIENT_PATTERNS:
        match = pattern.search(raw_text)
        if match and match.group(1):
            return match.group(1).strip().lower()

    historical_recipients = _unique_list(
        _normalize_list(profile.get("usual_recipients"))
        + _normalize_list(profile.get("typical_recipients"))
    )
    for recipient in historical_recipients:
        if recipient in text:
            return recipient
    return None


def _detect_urgency_term(text: str) -> str | None:
    for term in URGENCY_TERMS:
        if term.lower() in text:
            return term
    return None


def _classify_current_state(
    *,
    signature_fail: bool,
    is_anomalous: bool,
    high_risk_country_hit: bool,
    urgency_flag: bool,
    high_amount_flag: bool,
    recipient_out_of_pattern: bool,
    client_behavior: str,
) -> str:
    if (
        signature_fail
        or high_risk_country_hit
        or (urgency_flag and high_amount_flag and recipient_out_of_pattern)
        or client_behavior == "unusual"
    ):
        return "RISKY"
    if is_anomalous or urgency_flag or recipient_out_of_pattern:
        return "NORMAL"
    return "GOOD"


def _build_transition_matrix(
    *,
    stability_score: int,
    anomaly_weight: int,
    high_risk_signals: int,
    medium_risk_signals: int,
) -> dict[str, dict[str, float]]:
    stable = stability_score >= 2
    very_risky = high_risk_signals >= 3
    moderately_risky = (
        high_risk_signals >= 1
        or medium_risk_signals >= 2
        or anomaly_weight >= 2
    )

    matrix: dict[str, dict[str, float]] = {
        "GOOD": {"GOOD": 0.7, "NORMAL": 0.2, "RISKY": 0.08, "DEFAULT": 0.02},
        "NORMAL": {"GOOD": 0.2, "NORMAL": 0.55, "RISKY": 0.2, "DEFAULT": 0.05},
        "RISKY": {"GOOD": 0.05, "NORMAL": 0.2, "RISKY": 0.5, "DEFAULT": 0.25},
        "DEFAULT": {"GOOD": 0, "NORMAL": 0, "RISKY": 0, "DEFAULT": 1},
    }

    if stable:
        matrix["GOOD"] = {"GOOD": 0.8, "NORMAL": 0.15, "RISKY": 0.04, "DEFAULT": 0.01}
        matrix["NORMAL"] = {"GOOD": 0.3, "NORMAL": 0.5, "RISKY": 0.15, "DEFAULT": 0.05}

    if moderately_risky:
        matrix["NORMAL"] = {"GOOD": 0.12, "NORMAL": 0.42, "RISKY": 0.31, "DEFAULT": 0.15}
        matrix["RISKY"] = {"GOOD": 0.03, "NORMAL": 0.14, "RISKY": 0.48, "DEFAULT": 0.35}

    if very_risky:
        matrix["GOOD"] = {"GOOD": 0.45, "NORMAL": 0.2, "RISKY": 0.23, "DEFAULT": 0.12}
        matrix["NORMAL"] = {"GOOD": 0.08, "NORMAL": 0.27, "RISKY": 0.35, "DEFAULT": 0.3}
        matrix["RISKY"] = {"GOOD": 0.01, "NORMAL": 0.09, "RISKY": 0.4, "DEFAULT": 0.5}

    return matrix


def _multiply_distribution(
    distribution: dict[str, float],
    matrix: dict[str, dict[str, float]],
) -> dict[str, float]:
    next_dist: dict[str, float] = {"GOOD": 0, "NORMAL": 0, "RISKY": 0, "DEFAULT": 0}
    for from_state in STATES:
        for to_state in STATES:
            next_dist[to_state] += distribution[from_state] * matrix[from_state][to_state]
    return next_dist


def _calculate_markov_analysis(
    *,
    current_state: str,
    matrix: dict[str, dict[str, float]],
    high_risk_signals: int,
    medium_risk_signals: int,
    stability_score: int,
    anomaly_weight: int,
) -> dict[str, Any]:
    current_transitions = matrix[current_state]
    transition_probabilities = {
        s: _round_prob(current_transitions[s]) for s in STATES
    }

    # Start with all probability mass in current_state
    distribution: dict[str, float] = {s: 0.0 for s in STATES}
    distribution[current_state] = 1.0

    # 3-step look-ahead
    for _ in range(3):
        distribution = _multiply_distribution(distribution, matrix)

    probability_of_default = _round_prob(distribution["DEFAULT"])

    if probability_of_default >= 0.45:
        predicted_outcome = "high_risk_of_default"
    elif probability_of_default >= 0.2:
        predicted_outcome = "uncertain"
    else:
        predicted_outcome = "likely_to_repay"

    # Most-likely transition path
    path: list[str] = [current_state]
    active_state = current_state
    for _ in range(3):
        candidates = matrix[active_state]
        next_state = STATES[0]
        for state in STATES:
            if candidates[state] > candidates[next_state]:
                next_state = state
        path.append(next_state)
        active_state = next_state
        if active_state == "DEFAULT":
            break

    reasoning = (
        f"Current repayment state is {current_state}. "
        f"Behavior stability score is {stability_score} and anomaly weight is {anomaly_weight}. "
        f"Detected {high_risk_signals} high-risk signal(s) and {medium_risk_signals} medium-risk signal(s). "
        f"Most likely transition path is {' -> '.join(path)}. "
        f"Estimated default probability is {probability_of_default}."
    )

    return {
        "current_state": current_state,
        "transition_probabilities": transition_probabilities,
        "probability_of_default": probability_of_default,
        "predicted_outcome": predicted_outcome,
        "reasoning": reasoning,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_banking_compliance(
    transaction_text: str,
    client_profile: dict | None = None,
    signature_match: bool = True,
) -> dict[str, Any]:
    """Analyse a banking transaction for compliance risk.

    Parameters
    ----------
    transaction_text:
        Free-text description of the transaction (wire memo, payment
        instructions, etc.).
    client_profile:
        Optional dict with historical context about the client.  Recognised
        keys include ``usual_amount_min``, ``usual_amount_max``,
        ``min_amount``, ``max_amount``, ``average_amount``, ``avg_amount``,
        ``typical_countries``, ``usual_countries``, ``usual_recipients``,
        ``typical_recipients``, and ``high_amount_threshold``.
    signature_match:
        Whether the client's signature matches the specimen on file.

    Returns
    -------
    dict
        A structured result containing ``rules``, ``signature_verification``,
        ``behavior_analysis``, ``exit_risk``, ``overall_risk``, ``risk_score``,
        ``final_decision``, ``reasoning``, and ``markov_analysis``.
    """

    raw_text = transaction_text.strip() if isinstance(transaction_text, str) else ""
    text = raw_text.lower()
    profile: dict[str, Any] = (
        client_profile
        if isinstance(client_profile, dict)
        else {}
    )
    signature_matches: bool = bool(signature_match)

    # --- Detection helpers ---------------------------------------------------

    amount_info = _detect_amount(raw_text)
    detected_amount: float | None = amount_info["amount"]
    amount_source: str = amount_info["source"]

    detected_country = _detect_country(text, profile)
    detected_recipient = _detect_recipient(raw_text, text, profile)
    urgency_term = _detect_urgency_term(text)

    # --- Profile fields with fallbacks ---------------------------------------

    def _num_or_none(*keys: str) -> float | None:
        for k in keys:
            v = profile.get(k)
            if isinstance(v, (int, float)):
                return float(v)
        return None

    usual_amount_min = _num_or_none("usual_amount_min", "min_amount")
    usual_amount_max = _num_or_none("usual_amount_max", "max_amount")

    average_amount = _num_or_none("average_amount", "avg_amount")
    if average_amount is None and usual_amount_min is not None and usual_amount_max is not None:
        average_amount = (usual_amount_min + usual_amount_max) / 2

    typical_countries = _unique_list(
        _normalize_list(profile.get("typical_countries"))
        + _normalize_list(profile.get("usual_countries"))
    )

    usual_recipients = _unique_list(
        _normalize_list(profile.get("usual_recipients"))
        + _normalize_list(profile.get("typical_recipients"))
    )

    high_amount_threshold: float = (
        float(profile["high_amount_threshold"])
        if isinstance(profile.get("high_amount_threshold"), (int, float))
        else 10_000
    )

    # --- Derived flags -------------------------------------------------------

    new_recipient_term: str | None = next(
        (t for t in NEW_RECIPIENT_TERMS if t in text), None
    )
    vague_term: str | None = next(
        (t for t in VAGUE_TERMS if t in text), None
    )
    detail_term: str | None = next(
        (t for t in DETAIL_TERMS if t in text), None
    )

    high_risk_country_hit = bool(
        detected_country and detected_country in HIGH_RISK_COUNTRIES
    )
    medium_risk_country_hit = bool(
        detected_country
        and detected_country in MEDIUM_RISK_COUNTRIES
        and not high_risk_country_hit
    )

    high_amount_flag = detected_amount is not None and detected_amount >= high_amount_threshold

    recipient_out_of_pattern = bool(new_recipient_term) or (
        detected_recipient is not None
        and len(usual_recipients) > 0
        and detected_recipient not in usual_recipients
    )

    country_out_of_pattern = (
        detected_country is not None
        and len(typical_countries) > 0
        and detected_country not in typical_countries
    )

    amount_out_of_pattern_range = detected_amount is not None and (
        (usual_amount_min is not None and detected_amount < usual_amount_min)
        or (usual_amount_max is not None and detected_amount > usual_amount_max)
    )

    amount_out_of_pattern_average = (
        detected_amount is not None
        and average_amount is not None
        and (
            detected_amount >= average_amount * 2.5
            or detected_amount <= average_amount * 0.35
        )
    )

    strong_amount_deviation = (
        detected_amount is not None
        and average_amount is not None
        and detected_amount >= average_amount * 3
    )

    urgency_flag = bool(urgency_term)
    signature_fail = not signature_matches

    vague_details_flag = (
        not raw_text
        or len(raw_text) < 25
        or (not detail_term and bool(vague_term))
        or (not detail_term and len(raw_text.split()) < 5)
    )

    amount_out_of_pattern = amount_out_of_pattern_range or amount_out_of_pattern_average

    anomaly_weight = (
        (2 if strong_amount_deviation else (1 if amount_out_of_pattern else 0))
        + (1 if country_out_of_pattern else 0)
        + (1 if recipient_out_of_pattern else 0)
    )
    is_anomalous = anomaly_weight >= 2
    client_behavior = "unusual" if is_anomalous else "normal"

    # --- Rule evaluation -----------------------------------------------------

    rules: list[dict[str, str]] = []

    _add_rule(
        rules,
        "high_transaction_amount",
        high_amount_flag,
        (
            f'Detected amount {detected_amount} from "{amount_source}", '
            f"threshold {high_amount_threshold}."
            if detected_amount is not None
            else "No reliable amount detected in transaction text."
        ),
        weight=18,
    )

    if new_recipient_term:
        recipient_evidence = _make_snippet(raw_text, text, new_recipient_term)
    elif detected_recipient:
        if usual_recipients:
            recipient_evidence = (
                f'Recipient "{detected_recipient}" compared with known recipients: '
                f'{", ".join(usual_recipients)}.'
            )
        else:
            recipient_evidence = (
                f'Recipient "{detected_recipient}" detected, but no historical '
                f"recipient list was provided."
            )
    else:
        recipient_evidence = "No clear recipient detected in transaction text."

    _add_rule(rules, "unknown_or_new_recipient", recipient_out_of_pattern, recipient_evidence, weight=14)

    _add_rule(
        rules,
        "high_risk_country",
        high_risk_country_hit,
        (
            f'Detected country "{detected_country}".'
            if detected_country
            else "No destination country detected in transaction text."
        ),
        weight=18,
    )

    _add_rule(
        rules,
        "medium_risk_country",
        medium_risk_country_hit,
        (
            f'Medium-risk country detected in text: "{detected_country}".'
            if medium_risk_country_hit
            else "No medium-risk country detected in transaction text."
        ),
        weight=8,
    )

    if vague_details_flag:
        vague_evidence = (
            _make_snippet(raw_text, text, vague_term)
            if vague_term
            else "Transaction details are missing, too short, or lack a clear business purpose."
        )
    else:
        vague_evidence = (
            _make_snippet(raw_text, text, detail_term)
            if detail_term
            else raw_text[:140]
        )

    _add_rule(rules, "vague_or_missing_details", vague_details_flag, vague_evidence, weight=8)

    _add_rule(
        rules,
        "urgency_or_pressure_language",
        urgency_flag,
        (
            f'Matched urgency phrase: "{urgency_term}".'
            if urgency_flag
            else "No urgency or pressure language detected."
        ),
        weight=12,
    )

    _add_rule(
        rules,
        "signature_verification",
        signature_fail,
        (
            "Signature does not match the specimen."
            if signature_fail
            else "Signature matches the specimen."
        ),
        weight=20,
    )

    _add_rule(
        rules,
        "behavior_amount_vs_average",
        amount_out_of_pattern,
        (
            f"Amount {detected_amount} compared with client average {average_amount}."
            if detected_amount is not None and average_amount is not None
            else "Insufficient average transaction data for behavioral comparison."
        ),
        weight=18 if strong_amount_deviation else 12,
    )

    _add_rule(
        rules,
        "behavior_typical_countries",
        country_out_of_pattern,
        (
            (
                f'Country "{detected_country}" compared with typical countries: '
                f'{", ".join(typical_countries)}.'
                if typical_countries
                else f'Country "{detected_country}" detected, but no typical countries were provided.'
            )
            if detected_country
            else "No destination country available for behavioral comparison."
        ),
        weight=10,
    )

    _add_rule(
        rules,
        "behavior_usual_recipients",
        recipient_out_of_pattern,
        (
            (
                f'Recipient "{detected_recipient}" compared with usual recipients: '
                f'{", ".join(usual_recipients)}.'
                if usual_recipients
                else f'Recipient "{detected_recipient}" detected, but no usual recipients were provided.'
            )
            if detected_recipient
            else "No recipient available for behavioral comparison."
        ),
        weight=0,
    )

    # --- Exit-risk classification --------------------------------------------

    exit_risk: str
    if high_amount_flag and recipient_out_of_pattern and urgency_flag and is_anomalous:
        exit_risk = "high"
    else:
        exit_indicators = sum(
            [high_amount_flag, recipient_out_of_pattern, urgency_flag, is_anomalous]
        )
        if exit_indicators >= 3 or (signature_fail and exit_indicators >= 2):
            exit_risk = "medium"
        else:
            exit_risk = "low"

    suspicious_class: str
    if exit_risk == "high":
        suspicious_class = "potential exit fraud"
    elif any(
        [
            signature_fail,
            urgency_flag,
            amount_out_of_pattern,
            recipient_out_of_pattern,
            country_out_of_pattern,
            medium_risk_country_hit,
        ]
    ):
        suspicious_class = "suspicious activity"
    else:
        suspicious_class = "normal client"

    # --- Behavior summary ----------------------------------------------------

    if is_anomalous:
        behavior_details = (
            f"Strong deviation from normal behavior detected. "
            f"Amount anomaly={amount_out_of_pattern}, "
            f"country anomaly={country_out_of_pattern}, "
            f"recipient anomaly={recipient_out_of_pattern}. "
            f"Client behavior classified as {client_behavior}."
        )
    else:
        behavior_details = (
            "Transaction is broadly aligned with the client's known historical behavior."
        )

    # --- Aggregate risk score ------------------------------------------------

    risk_score = 0
    if high_amount_flag:
        risk_score += 18
    if recipient_out_of_pattern:
        risk_score += 14
    if high_risk_country_hit:
        risk_score += 18
    if medium_risk_country_hit:
        risk_score += 8
    if vague_details_flag:
        risk_score += 8
    if urgency_flag:
        risk_score += 12
    if signature_fail:
        risk_score += 20
    if amount_out_of_pattern:
        risk_score += 18 if strong_amount_deviation else 12
    if country_out_of_pattern:
        risk_score += 10
    if is_anomalous:
        risk_score += 12
    if exit_risk == "medium":
        risk_score += 10
    if exit_risk == "high":
        risk_score += 18
    risk_score = min(100, risk_score)

    # --- Overall decision ----------------------------------------------------

    overall_risk: str
    final_decision: str
    if risk_score > 45:
        overall_risk = "high"
        final_decision = "reject"
    elif risk_score > 20:
        overall_risk = "medium"
        final_decision = "review"
    else:
        overall_risk = "low"
        final_decision = "approve"

    # --- Markov analysis inputs ---------------------------------------------

    high_risk_signals = sum(
        [
            signature_fail,
            high_risk_country_hit,
            high_amount_flag,
            urgency_flag,
            is_anomalous,
            exit_risk == "high",
        ]
    )

    medium_risk_signals = sum(
        [
            medium_risk_country_hit,
            vague_details_flag,
            country_out_of_pattern,
            recipient_out_of_pattern,
            exit_risk == "medium",
        ]
    )

    stability_score = sum(
        [
            not signature_fail,
            not urgency_flag,
            not amount_out_of_pattern,
            not country_out_of_pattern,
            not recipient_out_of_pattern,
            client_behavior == "normal",
        ]
    )

    current_state = _classify_current_state(
        signature_fail=signature_fail,
        is_anomalous=is_anomalous,
        high_risk_country_hit=high_risk_country_hit,
        urgency_flag=urgency_flag,
        high_amount_flag=high_amount_flag,
        recipient_out_of_pattern=recipient_out_of_pattern,
        client_behavior=client_behavior,
    )

    transition_matrix = _build_transition_matrix(
        stability_score=stability_score,
        anomaly_weight=anomaly_weight,
        high_risk_signals=high_risk_signals,
        medium_risk_signals=medium_risk_signals,
    )

    markov_analysis = _calculate_markov_analysis(
        current_state=current_state,
        matrix=transition_matrix,
        high_risk_signals=high_risk_signals,
        medium_risk_signals=medium_risk_signals,
        stability_score=stability_score,
        anomaly_weight=anomaly_weight,
    )

    # --- Reasoning summary ---------------------------------------------------

    reasoning_parts = [
        f'Signature verification {"failed" if signature_fail else "passed"}.',
        (
            "Transaction amount is unusually high."
            if high_amount_flag
            else "Transaction amount is not materially high based on current thresholds."
        ),
        (
            "A high-risk country was detected."
            if high_risk_country_hit
            else (
                "A medium-risk country was detected."
                if medium_risk_country_hit
                else "No listed geographical risk country was detected."
            )
        ),
        (
            "Recipient appears new or inconsistent with historical behavior."
            if recipient_out_of_pattern
            else "Recipient appears consistent with historical behavior or insufficient recipient history was provided."
        ),
        (
            f'Urgency language was detected through the phrase "{urgency_term}".'
            if urgency_flag
            else "No urgency language detected."
        ),
        f"Behavior analysis marks the client as {client_behavior}.",
        f"Exit risk is {exit_risk}, leading to classification as {suspicious_class}.",
        f"Markov repayment model estimates default probability at {markov_analysis['probability_of_default']}.",
    ]

    return {
        "rules": rules,
        "signature_verification": "fail" if signature_fail else "pass",
        "behavior_analysis": {
            "is_anomalous": is_anomalous,
            "details": behavior_details,
        },
        "exit_risk": exit_risk,
        "overall_risk": overall_risk,
        "risk_score": risk_score,
        "final_decision": final_decision,
        "reasoning": " ".join(reasoning_parts),
        "markov_analysis": markov_analysis,
    }
