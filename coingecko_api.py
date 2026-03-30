"""
coingecko_api.py
CoinGecko Free API integration.
The API key is loaded from the database (user settings) — never exposed in the UI.
Free tier base URL: https://api.coingecko.com/api/v3
"""
import requests, time, os

_BASE = "https://api.coingecko.com/api/v3"
_cache: dict = {}
_PRICE_TTL   = 120   # 2 min cache for prices
_HISTORY_TTL = 600   # 10 min cache for history


def _get(endpoint, params, api_key, ttl=_PRICE_TTL):
    key = endpoint + str(sorted(params.items()))
    now = time.time()
    if key in _cache and now - _cache[key]["ts"] < ttl:
        return _cache[key]["data"]
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    try:
        r = requests.get(f"{_BASE}{endpoint}", params=params, headers=headers, timeout=12)
        if r.status_code == 429:
            return _cache.get(key, {}).get("data")
        r.raise_for_status()
        data = r.json()
        _cache[key] = {"data": data, "ts": now}
        return data
    except Exception:
        return _cache.get(key, {}).get("data")


def fetch_markets(api_key: str, limit: int = 25) -> list:
    """Top coins by market cap — used in Market Analysis."""
    data = _get("/coins/markets", {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h,7d",
    }, api_key, _PRICE_TTL)
    if not data:
        return []
    return [
        {
            "id":             c.get("id", ""),
            "symbol":         c.get("symbol", "").upper(),
            "name":           c.get("name", ""),
            "price":          c.get("current_price", 0) or 0,
            "market_cap":     c.get("market_cap", 0) or 0,
            "volume_24h":     c.get("total_volume", 0) or 0,
            "change_24h":     c.get("price_change_percentage_24h", 0) or 0,
            "change_7d":      c.get("price_change_percentage_7d_in_currency", 0) or 0,
            "image":          c.get("image", ""),
        }
        for c in data
    ]


def fetch_global(api_key: str) -> dict:
    """Global crypto market stats."""
    data = _get("/global", {}, api_key, 300)
    if not data or "data" not in data:
        return {}
    d = data["data"]
    return {
        "total_market_cap": d.get("total_market_cap", {}).get("usd", 0),
        "total_volume":     d.get("total_volume", {}).get("usd", 0),
        "btc_dominance":    round(d.get("market_cap_percentage", {}).get("btc", 0), 1),
        "market_cap_change":d.get("market_cap_change_percentage_24h_usd", 0),
        "active_coins":     d.get("active_cryptocurrencies", 0),
    }


def fetch_price(coin_id: str, api_key: str) -> float:
    """Single coin price."""
    data = _get("/simple/price", {"ids": coin_id, "vs_currencies": "usd"}, api_key)
    if data and coin_id in data:
        return data[coin_id].get("usd", 0)
    return 0.0


def fetch_prices_bulk(coin_ids: list, api_key: str) -> dict:
    """Bulk price fetch for portfolio holdings."""
    ids = ",".join(coin_ids)
    data = _get("/simple/price", {"ids": ids, "vs_currencies": "usd"}, api_key)
    if not data:
        return {}
    return {cid: data.get(cid, {}).get("usd", 0) for cid in coin_ids}


def fetch_history(coin_id: str, api_key: str, days: int = 30) -> list:
    """
    Historical daily prices for a coin.
    Returns list of [timestamp_ms, price] pairs.
    """
    data = _get(f"/coins/{coin_id}/market_chart",
                {"vs_currency": "usd", "days": days, "interval": "daily"},
                api_key, _HISTORY_TTL)
    if data and "prices" in data:
        return data["prices"]
    return []


def search_coins(query: str, api_key: str) -> list:
    """Search coins by name/symbol — used in add investment."""
    data = _get("/search", {"query": query}, api_key, 60)
    if not data or "coins" not in data:
        return []
    return [
        {"id": c["id"], "name": c["name"], "symbol": c["symbol"].upper()}
        for c in data["coins"][:10]
    ]


def validate_key(api_key: str) -> tuple:
    """Returns (is_valid, message)."""
    if not api_key or len(api_key) < 8:
        return False, "Key too short."
    data = _get("/ping", {}, api_key, 0)
    if data and "gecko_says" in data:
        return True, "API key is valid ✅"
    return False, "Invalid or rate-limited key."