"""core/risk_engine.py — shared math utilities"""
import numpy as np
import re


def parse_price(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        cleaned = re.sub(r"[^\d.]", "", str(value))
        return float(cleaned) if cleaned else None
    except (ValueError, TypeError):
        return None


def compute_volatility(prices: list) -> float:
    if len(prices) < 2:
        return 0.0
    arr = np.array(prices, dtype=float)
    log_returns = np.diff(np.log(arr + 1e-10))
    return float(np.std(log_returns) * np.sqrt(365))


def apply_diversification_rules(portfolio: dict, strategy: str = "balanced") -> dict:
    majors = {"bitcoin", "ethereum"}
    strategy_map = {
        "conservative": (0.70, 0.30),
        "balanced":     (0.50, 0.50),
        "aggressive":   (0.30, 0.70),
    }
    major_frac, alt_frac = strategy_map.get(strategy.lower(), (0.50, 0.50))
    coins = list(portfolio.keys())
    major_coins = [c for c in coins if c in majors]
    alt_coins   = [c for c in coins if c not in majors]
    result = {}
    if major_coins:
        per_major = major_frac / len(major_coins)
        for c in major_coins:
            result[c] = round(per_major * 100, 2)
    if alt_coins:
        per_alt = alt_frac / len(alt_coins)
        for c in alt_coins:
            result[c] = round(per_alt * 100, 2)
    return result