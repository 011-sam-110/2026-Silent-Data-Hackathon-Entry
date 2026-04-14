function analyzeBankingCompliance(transaction_text, client_profile, signature_match) {
  const rawText = typeof transaction_text === "string" ? transaction_text.trim() : "";
  const text = rawText.toLowerCase();
  const profile =
    client_profile && typeof client_profile === "object" ? client_profile : {};
  const signatureMatches = Boolean(signature_match);

  const STATES = ["GOOD", "NORMAL", "RISKY", "DEFAULT"];

  const highRiskCountries = [
    "iran",
    "north korea",
    "syria",
    "afghanistan",
    "myanmar",
    "russia",
    "belarus",
    "yemen",
    "somalia",
    "venezuela"
  ];

  const mediumRiskCountries = [
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
    "vietnam"
  ];

  const urgencyTerms = [
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
    "limited availability"
  ];

  const vagueTerms = [
    "misc",
    "miscellaneous",
    "other",
    "support",
    "personal",
    "project",
    "general payment",
    "business matter",
    "help",
    "services"
  ];

  const detailTerms = [
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
    "payment for"
  ];

  function normalizeList(value) {
    if (!Array.isArray(value)) {
      return [];
    }

    return value
      .map((item) => String(item).trim().toLowerCase())
      .filter(Boolean);
  }

  function uniqueList(items) {
    return [...new Set(items)];
  }

  function roundProbability(value) {
    return Number(Math.max(0, Math.min(1, value)).toFixed(4));
  }

  function makeSnippet(match) {
    if (!rawText) {
      return "No transaction text provided.";
    }

    if (!match) {
      return rawText.slice(0, 140);
    }

    const phrase = String(match).toLowerCase();
    const startIndex = text.indexOf(phrase);
    if (startIndex === -1) {
      return rawText.slice(0, 140);
    }

    const start = Math.max(0, startIndex - 30);
    const end = Math.min(rawText.length, startIndex + phrase.length + 40);
    return rawText.slice(start, end);
  }

  function addRule(rules, rule, failed, evidence) {
    rules.push({
      rule,
      status: failed ? "fail" : "pass",
      evidence
    });
  }

  function detectAmount() {
    const patterns = [
      /\b(?:usd|gbp|eur|\$)\s?(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?\b/i,
      /\b(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{2})?\s?(?:usd|gbp|eur|dollars|pounds|euros)\b/i,
      /\b(\d{5,})(?:\.\d{2})?\b/
    ];

    for (const pattern of patterns) {
      const match = rawText.match(pattern);
      if (!match) {
        continue;
      }

      const amount = Number(String(match[1]).replace(/,/g, ""));
      if (!Number.isNaN(amount)) {
        return { amount, source: match[0] };
      }
    }

    return { amount: null, source: "" };
  }

  function detectCountry() {
    const knownCountries = uniqueList([
      ...highRiskCountries,
      ...mediumRiskCountries,
      ...normalizeList(profile.typical_countries),
      ...normalizeList(profile.usual_countries),
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
      "switzerland"
    ]);

    for (const country of knownCountries) {
      if (text.includes(country)) {
        return country;
      }
    }

    return null;
  }

  function detectRecipient() {
    const explicitPatterns = [
      /\bbeneficiary[:\s]+([a-z0-9&.\- ]{3,40}?)(?=\s+(?:in|for|from|regarding)\b|$|,)/i,
      /\brecipient[:\s]+([a-z0-9&.\- ]{3,40}?)(?=\s+(?:in|for|from|regarding)\b|$|,)/i,
      /\bpayee[:\s]+([a-z0-9&.\- ]{3,40}?)(?=\s+(?:in|for|from|regarding)\b|$|,)/i,
      /\bto\s+([A-Z][A-Za-z0-9&.\- ]{2,40}?)(?=\s+(?:in|for|from|regarding)\b|$|,)/
    ];

    for (const pattern of explicitPatterns) {
      const match = rawText.match(pattern);
      if (match && match[1]) {
        return match[1].trim().toLowerCase();
      }
    }

    const historicalRecipients = uniqueList([
      ...normalizeList(profile.usual_recipients),
      ...normalizeList(profile.typical_recipients)
    ]);

    for (const recipient of historicalRecipients) {
      if (text.includes(recipient)) {
        return recipient;
      }
    }

    return null;
  }

  function detectUrgencyTerm() {
    for (const term of urgencyTerms) {
      if (text.includes(term.toLowerCase())) {
        return term;
      }
    }
    return null;
  }

  function classifyCurrentState(params) {
    const {
      signatureFail,
      isAnomalous,
      highRiskCountryHit,
      urgencyFlag,
      highAmountFlag,
      recipientOutOfPattern,
      clientBehavior
    } = params;

    if (
      signatureFail ||
      highRiskCountryHit ||
      (urgencyFlag && highAmountFlag && recipientOutOfPattern) ||
      clientBehavior === "unusual"
    ) {
      return "RISKY";
    }

    if (isAnomalous || urgencyFlag || recipientOutOfPattern) {
      return "NORMAL";
    }

    return "GOOD";
  }

  function buildTransitionMatrix(params) {
    const {
      stabilityScore,
      anomalyWeight,
      highRiskSignals,
      mediumRiskSignals
    } = params;

    const stable = stabilityScore >= 2;
    const veryRisky = highRiskSignals >= 3;
    const moderatelyRisky = highRiskSignals >= 1 || mediumRiskSignals >= 2 || anomalyWeight >= 2;

    const matrix = {
      GOOD: { GOOD: 0.7, NORMAL: 0.2, RISKY: 0.08, DEFAULT: 0.02 },
      NORMAL: { GOOD: 0.2, NORMAL: 0.55, RISKY: 0.2, DEFAULT: 0.05 },
      RISKY: { GOOD: 0.05, NORMAL: 0.2, RISKY: 0.5, DEFAULT: 0.25 },
      DEFAULT: { GOOD: 0, NORMAL: 0, RISKY: 0, DEFAULT: 1 }
    };

    if (stable) {
      matrix.GOOD = { GOOD: 0.8, NORMAL: 0.15, RISKY: 0.04, DEFAULT: 0.01 };
      matrix.NORMAL = { GOOD: 0.3, NORMAL: 0.5, RISKY: 0.15, DEFAULT: 0.05 };
    }

    if (moderatelyRisky) {
      matrix.NORMAL = { GOOD: 0.12, NORMAL: 0.42, RISKY: 0.31, DEFAULT: 0.15 };
      matrix.RISKY = { GOOD: 0.03, NORMAL: 0.14, RISKY: 0.48, DEFAULT: 0.35 };
    }

    if (veryRisky) {
      matrix.GOOD = { GOOD: 0.45, NORMAL: 0.2, RISKY: 0.23, DEFAULT: 0.12 };
      matrix.NORMAL = { GOOD: 0.08, NORMAL: 0.27, RISKY: 0.35, DEFAULT: 0.3 };
      matrix.RISKY = { GOOD: 0.01, NORMAL: 0.09, RISKY: 0.4, DEFAULT: 0.5 };
    }

    return matrix;
  }

  function multiplyDistribution(distribution, matrix) {
    const next = { GOOD: 0, NORMAL: 0, RISKY: 0, DEFAULT: 0 };

    for (const fromState of STATES) {
      for (const toState of STATES) {
        next[toState] += distribution[fromState] * matrix[fromState][toState];
      }
    }

    return next;
  }

  function calculateMarkovAnalysis(params) {
    const {
      currentState,
      matrix,
      highRiskSignals,
      mediumRiskSignals,
      stabilityScore,
      anomalyWeight
    } = params;

    const currentTransitions = matrix[currentState];
    const transitionProbabilities = {
      GOOD: roundProbability(currentTransitions.GOOD),
      NORMAL: roundProbability(currentTransitions.NORMAL),
      RISKY: roundProbability(currentTransitions.RISKY),
      DEFAULT: roundProbability(currentTransitions.DEFAULT)
    };

    let distribution = {
      GOOD: 0,
      NORMAL: 0,
      RISKY: 0,
      DEFAULT: 0
    };
    distribution[currentState] = 1;

    for (let i = 0; i < 3; i += 1) {
      distribution = multiplyDistribution(distribution, matrix);
    }

    const probabilityOfDefault = roundProbability(distribution.DEFAULT);

    let predictedOutcome = "likely_to_repay";
    if (probabilityOfDefault >= 0.45) {
      predictedOutcome = "high_risk_of_default";
    } else if (probabilityOfDefault >= 0.2) {
      predictedOutcome = "uncertain";
    }

    const path = [currentState];
    let activeState = currentState;
    for (let step = 0; step < 3; step += 1) {
      const candidates = matrix[activeState];
      const nextState = STATES.reduce((best, state) =>
        candidates[state] > candidates[best] ? state : best
      , STATES[0]);
      path.push(nextState);
      activeState = nextState;
      if (activeState === "DEFAULT") {
        break;
      }
    }

    const reasoning = [
      `Current repayment state is ${currentState}.`,
      `Behavior stability score is ${stabilityScore} and anomaly weight is ${anomalyWeight}.`,
      `Detected ${highRiskSignals} high-risk signal(s) and ${mediumRiskSignals} medium-risk signal(s).`,
      `Most likely transition path is ${path.join(" -> ")}.`,
      `Estimated default probability is ${probabilityOfDefault}.`
    ].join(" ");

    return {
      current_state: currentState,
      transition_probabilities: transitionProbabilities,
      probability_of_default: probabilityOfDefault,
      predicted_outcome: predictedOutcome,
      reasoning
    };
  }

  const { amount: detectedAmount, source: amountSource } = detectAmount();
  const detectedCountry = detectCountry();
  const detectedRecipient = detectRecipient();
  const urgencyTerm = detectUrgencyTerm();

  const usualAmountMin =
    typeof profile.usual_amount_min === "number"
      ? profile.usual_amount_min
      : typeof profile.min_amount === "number"
        ? profile.min_amount
        : null;

  const usualAmountMax =
    typeof profile.usual_amount_max === "number"
      ? profile.usual_amount_max
      : typeof profile.max_amount === "number"
        ? profile.max_amount
        : null;

  const averageAmount =
    typeof profile.average_amount === "number"
      ? profile.average_amount
      : typeof profile.avg_amount === "number"
        ? profile.avg_amount
        : usualAmountMin !== null && usualAmountMax !== null
          ? (usualAmountMin + usualAmountMax) / 2
          : null;

  const typicalCountries = uniqueList([
    ...normalizeList(profile.typical_countries),
    ...normalizeList(profile.usual_countries)
  ]);

  const usualRecipients = uniqueList([
    ...normalizeList(profile.usual_recipients),
    ...normalizeList(profile.typical_recipients)
  ]);

  const highAmountThreshold =
    typeof profile.high_amount_threshold === "number"
      ? profile.high_amount_threshold
      : 10000;

  const explicitNewRecipientTerms = [
    "new recipient",
    "new payee",
    "new beneficiary",
    "first time recipient",
    "first time payment",
    "never paid before",
    "unknown recipient",
    "unfamiliar account"
  ];

  const newRecipientTerm = explicitNewRecipientTerms.find((term) =>
    text.includes(term)
  );
  const vagueTerm = vagueTerms.find((term) => text.includes(term));
  const detailTerm = detailTerms.find((term) => text.includes(term));

  const highRiskCountryHit =
    detectedCountry && highRiskCountries.includes(detectedCountry);
  const mediumRiskCountryHit =
    detectedCountry &&
    mediumRiskCountries.includes(detectedCountry) &&
    !highRiskCountryHit;

  const highAmountFlag =
    detectedAmount !== null && detectedAmount >= highAmountThreshold;

  const recipientOutOfPattern =
    Boolean(newRecipientTerm) ||
    (detectedRecipient !== null &&
      usualRecipients.length > 0 &&
      !usualRecipients.includes(detectedRecipient));

  const countryOutOfPattern =
    detectedCountry !== null &&
    typicalCountries.length > 0 &&
    !typicalCountries.includes(detectedCountry);

  const amountOutOfPatternRange =
    detectedAmount !== null &&
    ((usualAmountMin !== null && detectedAmount < usualAmountMin) ||
      (usualAmountMax !== null && detectedAmount > usualAmountMax));

  const amountOutOfPatternAverage =
    detectedAmount !== null &&
    averageAmount !== null &&
    (detectedAmount >= averageAmount * 2.5 || detectedAmount <= averageAmount * 0.35);

  const strongAmountDeviation =
    detectedAmount !== null &&
    averageAmount !== null &&
    detectedAmount >= averageAmount * 3;

  const urgencyFlag = Boolean(urgencyTerm);
  const signatureFail = !signatureMatches;

  const vagueDetailsFlag =
    !rawText ||
    rawText.length < 25 ||
    (!detailTerm && Boolean(vagueTerm)) ||
    (!detailTerm && rawText.split(/\s+/).length < 5);

  const amountOutOfPattern = amountOutOfPatternRange || amountOutOfPatternAverage;

  const anomalyWeight =
    (strongAmountDeviation ? 2 : amountOutOfPattern ? 1 : 0) +
    (countryOutOfPattern ? 1 : 0) +
    (recipientOutOfPattern ? 1 : 0);
  const isAnomalous = anomalyWeight >= 2;
  const clientBehavior = isAnomalous ? "unusual" : "normal";

  const rules = [];

  addRule(
    rules,
    "high_transaction_amount",
    highAmountFlag,
    detectedAmount !== null
      ? `Detected amount ${detectedAmount} from "${amountSource}", threshold ${highAmountThreshold}.`
      : "No reliable amount detected in transaction text."
  );

  addRule(
    rules,
    "unknown_or_new_recipient",
    recipientOutOfPattern,
    newRecipientTerm
      ? makeSnippet(newRecipientTerm)
      : detectedRecipient
        ? usualRecipients.length > 0
          ? `Recipient "${detectedRecipient}" compared with known recipients: ${usualRecipients.join(", ")}.`
          : `Recipient "${detectedRecipient}" detected, but no historical recipient list was provided.`
        : "No clear recipient detected in transaction text."
  );

  addRule(
    rules,
    "high_risk_country",
    Boolean(highRiskCountryHit),
    detectedCountry
      ? `Detected country "${detectedCountry}".`
      : "No destination country detected in transaction text."
  );

  addRule(
    rules,
    "medium_risk_country",
    Boolean(mediumRiskCountryHit),
    mediumRiskCountryHit
      ? `Medium-risk country detected in text: "${detectedCountry}".`
      : "No medium-risk country detected in transaction text."
  );

  addRule(
    rules,
    "vague_or_missing_details",
    vagueDetailsFlag,
    vagueDetailsFlag
      ? vagueTerm
        ? makeSnippet(vagueTerm)
        : "Transaction details are missing, too short, or lack a clear business purpose."
      : detailTerm
        ? makeSnippet(detailTerm)
        : rawText.slice(0, 140)
  );

  addRule(
    rules,
    "urgency_or_pressure_language",
    urgencyFlag,
    urgencyFlag
      ? `Matched urgency phrase: "${urgencyTerm}".`
      : "No urgency or pressure language detected."
  );

  addRule(
    rules,
    "signature_verification",
    signatureFail,
    signatureFail
      ? "Signature does not match the specimen."
      : "Signature matches the specimen."
  );

  addRule(
    rules,
    "behavior_amount_vs_average",
    amountOutOfPattern,
    detectedAmount !== null && averageAmount !== null
      ? `Amount ${detectedAmount} compared with client average ${averageAmount}.`
      : "Insufficient average transaction data for behavioral comparison."
  );

  addRule(
    rules,
    "behavior_typical_countries",
    countryOutOfPattern,
    detectedCountry
      ? typicalCountries.length > 0
        ? `Country "${detectedCountry}" compared with typical countries: ${typicalCountries.join(", ")}.`
        : `Country "${detectedCountry}" detected, but no typical countries were provided.`
      : "No destination country available for behavioral comparison."
  );

  addRule(
    rules,
    "behavior_usual_recipients",
    recipientOutOfPattern,
    detectedRecipient
      ? usualRecipients.length > 0
        ? `Recipient "${detectedRecipient}" compared with usual recipients: ${usualRecipients.join(", ")}.`
        : `Recipient "${detectedRecipient}" detected, but no usual recipients were provided.`
      : "No recipient available for behavioral comparison."
  );

  let exitRisk = "low";
  if (highAmountFlag && recipientOutOfPattern && urgencyFlag && isAnomalous) {
    exitRisk = "high";
  } else {
    const exitIndicators = [
      highAmountFlag,
      recipientOutOfPattern,
      urgencyFlag,
      isAnomalous
    ].filter(Boolean).length;

    if (exitIndicators >= 3 || (signatureFail && exitIndicators >= 2)) {
      exitRisk = "medium";
    }
  }

  let suspiciousClass = "normal client";
  if (exitRisk === "high") {
    suspiciousClass = "potential exit fraud";
  } else if (
    signatureFail ||
    urgencyFlag ||
    amountOutOfPattern ||
    recipientOutOfPattern ||
    countryOutOfPattern ||
    mediumRiskCountryHit
  ) {
    suspiciousClass = "suspicious activity";
  }

  const behaviorDetails = isAnomalous
    ? `Strong deviation from normal behavior detected. Amount anomaly=${amountOutOfPattern}, country anomaly=${countryOutOfPattern}, recipient anomaly=${recipientOutOfPattern}. Client behavior classified as ${clientBehavior}.`
    : "Transaction is broadly aligned with the client's known historical behavior.";

  let riskScore = 0;
  if (highAmountFlag) riskScore += 18;
  if (recipientOutOfPattern) riskScore += 14;
  if (highRiskCountryHit) riskScore += 18;
  if (mediumRiskCountryHit) riskScore += 8;
  if (vagueDetailsFlag) riskScore += 8;
  if (urgencyFlag) riskScore += 12;
  if (signatureFail) riskScore += 20;
  if (amountOutOfPattern) riskScore += strongAmountDeviation ? 18 : 12;
  if (countryOutOfPattern) riskScore += 10;
  if (isAnomalous) riskScore += 12;
  if (exitRisk === "medium") riskScore += 10;
  if (exitRisk === "high") riskScore += 18;
  riskScore = Math.min(100, riskScore);

  let overallRisk = "low";
  let finalDecision = "approve";

  if (signatureFail || exitRisk === "high" || highRiskCountryHit || riskScore >= 75) {
    overallRisk = "high";
    finalDecision = "reject";
  } else if (
    riskScore >= 35 ||
    isAnomalous ||
    mediumRiskCountryHit ||
    exitRisk === "medium"
  ) {
    overallRisk = "medium";
    finalDecision = "review";
  }

  const highRiskSignals = [
    signatureFail,
    highRiskCountryHit,
    highAmountFlag,
    urgencyFlag,
    isAnomalous,
    exitRisk === "high"
  ].filter(Boolean).length;

  const mediumRiskSignals = [
    mediumRiskCountryHit,
    vagueDetailsFlag,
    countryOutOfPattern,
    recipientOutOfPattern,
    exitRisk === "medium"
  ].filter(Boolean).length;

  const stabilityScore = [
    !signatureFail,
    !urgencyFlag,
    !amountOutOfPattern,
    !countryOutOfPattern,
    !recipientOutOfPattern,
    clientBehavior === "normal"
  ].filter(Boolean).length;

  const currentState = classifyCurrentState({
    signatureFail,
    isAnomalous,
    highRiskCountryHit,
    urgencyFlag,
    highAmountFlag,
    recipientOutOfPattern,
    clientBehavior
  });

  const transitionMatrix = buildTransitionMatrix({
    stabilityScore,
    anomalyWeight,
    highRiskSignals,
    mediumRiskSignals
  });

  const markovAnalysis = calculateMarkovAnalysis({
    currentState,
    matrix: transitionMatrix,
    highRiskSignals,
    mediumRiskSignals,
    stabilityScore,
    anomalyWeight
  });

  const reasoningParts = [
    `Signature verification ${signatureFail ? "failed" : "passed"}.`,
    highAmountFlag
      ? "Transaction amount is unusually high."
      : "Transaction amount is not materially high based on current thresholds.",
    highRiskCountryHit
      ? "A high-risk country was detected."
      : mediumRiskCountryHit
        ? "A medium-risk country was detected."
        : "No listed geographical risk country was detected.",
    recipientOutOfPattern
      ? "Recipient appears new or inconsistent with historical behavior."
      : "Recipient appears consistent with historical behavior or insufficient recipient history was provided.",
    urgencyFlag
      ? `Urgency language was detected through the phrase "${urgencyTerm}".`
      : "No urgency language detected.",
    `Behavior analysis marks the client as ${clientBehavior}.`,
    `Exit risk is ${exitRisk}, leading to classification as ${suspiciousClass}.`,
    `Markov repayment model estimates default probability at ${markovAnalysis.probability_of_default}.`
  ];

  return {
    rules,
    signature_verification: signatureFail ? "fail" : "pass",
    behavior_analysis: {
      is_anomalous: isAnomalous,
      details: behaviorDetails
    },
    exit_risk: exitRisk,
    overall_risk: overallRisk,
    risk_score: riskScore,
    final_decision: finalDecision,
    reasoning: reasoningParts.join(" "),
    markov_analysis: markovAnalysis
  };
}

module.exports = {
  analyzeBankingCompliance
};
