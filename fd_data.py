"""
FD Bank Data - Blostem Partner Banks
Rates sourced from public data (as of Q1 2026)
"""

FD_BANKS = [
    {
        "id": "suryoday",
        "name": "Suryoday Small Finance Bank",
        "short": "Suryoday SFB",
        "rating": "AA",
        "type": "Small Finance Bank",
        "rates": {
            "3": 6.75, "6": 7.25, "9": 7.50, "12": 8.25,
            "18": 8.50, "24": 8.35, "36": 8.10
        },
        "min_amount": 1000,
        "dicgc": True,
        "color": "#FF6B35"
    },
    {
        "id": "unity",
        "name": "Unity Small Finance Bank",
        "short": "Unity SFB",
        "rating": "AA",
        "type": "Small Finance Bank",
        "rates": {
            "3": 6.50, "6": 7.00, "9": 7.35, "12": 8.15,
            "18": 8.40, "24": 8.20, "36": 7.90
        },
        "min_amount": 1000,
        "dicgc": True,
        "color": "#4ECDC4"
    },
    {
        "id": "utkarsh",
        "name": "Utkarsh Small Finance Bank",
        "short": "Utkarsh SFB",
        "rating": "AA",
        "type": "Small Finance Bank",
        "rates": {
            "3": 6.60, "6": 7.10, "9": 7.40, "12": 8.10,
            "18": 8.30, "24": 8.15, "36": 7.85
        },
        "min_amount": 1000,
        "dicgc": True,
        "color": "#45B7D1"
    },
    {
        "id": "shivalik",
        "name": "Shivalik Small Finance Bank",
        "short": "Shivalik SFB",
        "rating": "A+",
        "type": "Small Finance Bank",
        "rates": {
            "3": 6.40, "6": 6.90, "9": 7.25, "12": 8.00,
            "18": 8.20, "24": 8.00, "36": 7.75
        },
        "min_amount": 1000,
        "dicgc": True,
        "color": "#96CEB4"
    },
    {
        "id": "shriram",
        "name": "Shriram Finance",
        "short": "Shriram",
        "rating": "AA+",
        "type": "NBFC",
        "rates": {
            "3": 7.00, "6": 7.50, "9": 7.75, "12": 8.30,
            "18": 8.45, "24": 8.50, "36": 8.25
        },
        "min_amount": 5000,
        "dicgc": False,
        "color": "#FFEAA7"
    },
    {
        "id": "bajaj",
        "name": "Bajaj Finance",
        "short": "Bajaj Finance",
        "rating": "AAA",
        "type": "NBFC",
        "rates": {
            "3": 7.15, "6": 7.60, "9": 7.80, "12": 8.35,
            "18": 8.50, "24": 8.55, "36": 8.30
        },
        "min_amount": 15000,
        "dicgc": False,
        "color": "#DDA0DD"
    },
    {
        "id": "mahindra",
        "name": "Mahindra Finance",
        "short": "Mahindra",
        "rating": "AA+",
        "type": "NBFC",
        "rates": {
            "3": 6.90, "6": 7.40, "9": 7.65, "12": 8.20,
            "18": 8.35, "24": 8.40, "36": 8.15
        },
        "min_amount": 5000,
        "dicgc": False,
        "color": "#F0E68C"
    },
    {
        "id": "jana",
        "name": "Jana Small Finance Bank",
        "short": "Jana SFB",
        "rating": "A+",
        "type": "Small Finance Bank",
        "rates": {
            "3": 6.30, "6": 6.85, "9": 7.20, "12": 7.90,
            "18": 8.10, "24": 7.95, "36": 7.65
        },
        "min_amount": 1000,
        "dicgc": True,
        "color": "#87CEEB"
    }
]


def get_rbi_rate_prediction() -> dict:
    """
    Simulated RBI rate cycle prediction.
    In production: would use ML model trained on RBI meeting outcomes,
    inflation data (CPI), GDP growth, and Fed rate signals.
    """
    return {
        "current_repo_rate": 6.25,
        "prediction": "hold",
        "confidence": 72,
        "signal": "neutral",
        "next_meeting": "June 2026",
        "recommendation": "BOOK NOW",
        "reasoning": (
            "Inflation remains within RBI's 4% ± 2% comfort zone. "
            "With global central banks pausing, RBI likely to hold through Q2 2026. "
            "Current FD rates near cycle peak — favorable booking window."
        ),
        "rate_outlook_3m": "stable",
        "rate_outlook_6m": "slight_decline",
        "rate_outlook_12m": "decline",
        "optimal_tenure_signal": "12-18 months to lock in current rates",
        "risk_factors": [
            "US Fed rate decisions",
            "Monsoon impact on food inflation",
            "Global crude oil prices"
        ]
    }


def get_tax_optimization(amount: float, annual_return_pct: float) -> dict:
    """
    Tax optimization advice based on FD amount and expected returns.
    """
    estimated_interest = amount * (annual_return_pct / 100)
    tds_threshold = 40000  # ₹40,000 for regular (₹50,000 for seniors)

    advice = []
    forms_needed = []

    if estimated_interest < tds_threshold:
        advice.append("Your interest income is below TDS threshold — no TDS will be deducted.")
    else:
        tds_amount = estimated_interest * 0.10
        advice.append(f"Estimated TDS: ₹{tds_amount:,.0f} will be deducted at 10% by banks.")
        advice.append("Submit Form 15G (if income below taxable limit) to avoid TDS deduction.")
        forms_needed.append("Form 15G")

    if amount > 500000:
        advice.append("Amount exceeds DICGC limit of ₹5L — split across banks for full coverage.")

    if estimated_interest > 250000:
        advice.append("Consider distributing FDs across financial years to manage tax liability.")

    return {
        "estimated_annual_interest": round(estimated_interest, 2),
        "tds_applicable": estimated_interest >= tds_threshold,
        "tds_threshold": tds_threshold,
        "forms_recommended": forms_needed,
        "advice": advice,
        "tip": "Senior citizens (60+) get higher TDS threshold of ₹50,000 and often 0.25-0.50% higher rates."
    }
