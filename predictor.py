"""
predictor.py
7-day price forecast using Scikit-Learn LinearRegression.
X = date ordinal, y = closing price.
"""
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from core.risk_engine import parse_price


def predict_7days(prices_ts: list) -> tuple:
    """
    prices_ts: list of [timestamp_ms, price] from CoinGecko.
    Returns (future_dates: list[str], predicted_prices: list[float]) or (None, None).
    """
    if not prices_ts or len(prices_ts) < 7:
        return None, None

    df = pd.DataFrame(prices_ts, columns=["ts", "price"])
    df["date"] = pd.to_datetime(df["ts"], unit="ms")
    df.sort_values("date", inplace=True)
    df.dropna(subset=["price"], inplace=True)
    df["ordinal"] = df["date"].map(lambda d: d.toordinal())

    X = df[["ordinal"]].values
    y = df["price"].values

    model = LinearRegression()
    model.fit(X, y)

    last_date = df["date"].max()
    future_dates = [last_date + timedelta(days=i + 1) for i in range(7)]
    future_ords  = np.array([[d.toordinal()] for d in future_dates])
    preds = np.maximum(model.predict(future_ords), 0)

    return (
        [d.strftime("%b %d") for d in future_dates],
        [round(float(p), 4) for p in preds],
    )