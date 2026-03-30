"""
app.py — CryptoPortfolio Manager
  

"""

# Standard library
import io
import os
from datetime import datetime

# Third-party
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv          
from reportlab.lib import colors as rc
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Local modules
import database_manager as db
from coingecko_api import fetch_global, fetch_history, fetch_markets, fetch_prices_bulk
from core.risk_engine import apply_diversification_rules
from notifications import send_alert
from predictor import predict_7days

# THIS LINKS YOUR APP TO YOUR NEW STYLES.PY FILE
from styles import CSS_THEME 

 
# API SECURITY SETUP
 
load_dotenv()

def api_key() -> str:
    """Return the CoinGecko API key from the environment. Never logs or displays it."""
    return os.getenv("COINGECKO_API_KEY", "")


 
# CONSTANTS
 

COINS = {
    "bitcoin": "Bitcoin", "ethereum": "Ethereum", "litecoin": "Litecoin",
    "dogecoin": "Dogecoin", "cardano": "Cardano", "solana": "Solana",
    "xrp": "XRP", "binancecoin": "BNB", "polkadot": "Polkadot",
    "avalanche-2": "Avalanche", "chainlink": "Chainlink", "tron": "TRON",
}

G = "#059669"   # green  (profit / rising)
R = "#DC2626"   # red    (loss / falling)
B = "#047857"   # brand emerald

PALETTE = [
    "#047857", "#10B981", "#F59E0B", "#6366F1", "#EC4899",
    "#64748B", "#06B6D4", "#84CC16", "#F97316", "#EF4444", "#8B5CF6", "#22C55E",
]

 
# PLOTLY LAYOUT HELPER
 

def chart_layout(**overrides) -> dict:
    """Build a Plotly layout dict with safe deep-merge to prevent UI crashes."""
    base = {
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor":  "#F8FAFC",
        "font":   {"family": "Inter, sans-serif", "color": "#374151", "size": 12},
        "margin": {"t": 48, "b": 40, "l": 48, "r": 20},
        "xaxis":  {"gridcolor": "rgba(0,0,0,0.05)", "linecolor": "rgba(0,0,0,0.1)",
                   "tickfont":  {"color": "#6B7280", "size": 11}, "showgrid": True},
        "yaxis":  {"gridcolor": "rgba(0,0,0,0.05)", "linecolor": "rgba(0,0,0,0.1)",
                   "tickfont":  {"color": "#6B7280", "size": 11}, "showgrid": True},
        "legend": {"font": {"color": "#374151", "size": 12},
                   "bgcolor": "rgba(255,255,255,0.9)",
                   "bordercolor": "#E5E7EB", "borderwidth": 1},
        "hoverlabel": {"bgcolor": "#FFFFFF", "bordercolor": "#E5E7EB",
                       "font_color": "#111827", "font_size": 12},
    }
    for k, v in overrides.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            base[k] = {**base[k], **v}   
        else:
            base[k] = v                   
    return base


 
# STREAMLIT APP SETUP
 

st.set_page_config(page_title="CryptoPortfolio", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

# THIS INJECTS YOUR BEAUTIFUL CSS THEME
st.markdown(f"<style>{CSS_THEME}</style>", unsafe_allow_html=True) 

db.init_db()

for _k, _v in {"logged_in": False, "user": None, "page": "Dashboard",
                "live_prices": {}}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


 
# UTILITY FUNCTIONS
 

def live_price(coin_id: str) -> float:
    return st.session_state.live_prices.get(coin_id, 0.0)

def fmt(p: float) -> str:
    if p >= 100: return f"${p:,.2f}"
    if p >= 1:   return f"${p:,.4f}"
    if p > 0:    return f"${p:,.6f}"
    return "—"   

def badge(value: float, suffix: str = "%") -> str:
    sign = "+" if value >= 0 else ""
    clr  = G if value >= 0 else R
    bg   = "#ECFDF5" if value >= 0 else "#FEF2F2"
    return (f"<span style='background:{bg};color:{clr};font-size:.8rem;"
            f"font-weight:600;padding:2px 9px;border-radius:9999px;'>"
            f"{sign}{value:.2f}{suffix}</span>")

def section_header(title: str, subtitle: str = "") -> None:
    sub = (f"<p style='margin:.3rem 0 0;font-size:.9375rem;color:#64748B;'>"
           f"{subtitle}</p>") if subtitle else ""
    st.markdown(
        f"<div style='margin-bottom:1.75rem;padding-bottom:1rem;"
        f"border-bottom:1px solid #E2E8F0;'>"
        f"<h1 style='margin:0;font-size:1.75rem;font-weight:700;color:#047857;'>"
        f"{title}</h1>{sub}</div>",
        unsafe_allow_html=True,
    )

def sync_live_prices() -> bool:
    """Fetch current prices from CoinGecko with robust error handling."""
    key = api_key()
    if not key:
        st.sidebar.error("API Key missing in .env file.")
        return False
    
    try:
        prices = fetch_prices_bulk(list(COINS.keys()), key)
        if not prices:
            st.sidebar.warning("CoinGecko returned empty data. Check rate limits.")
            return False
        st.session_state.live_prices = prices
        for cid, p in prices.items():
            db.save_price(cid, p)
        return True
    except Exception as e:
        st.sidebar.error(f"API Error: {str(e)}")
        return False


def compute_portfolio_rows(holdings: list) -> tuple:
    rows, total_val, total_cost = [], 0.0, 0.0
    for h in holdings:
        lp   = live_price(h["coin_id"])
        val  = h["quantity"] * lp
        cost = h["quantity"] * h["purchase_price"]
        roi  = ((lp - h["purchase_price"]) / h["purchase_price"] * 100
                if h["purchase_price"] > 0 else 0)
        rows.append({**h, "live_price": lp, "live_value": val,
                     "cost": cost, "roi": roi, "pl": val - cost})
        total_val  += val
        total_cost += cost
    return rows, total_val, total_cost


 
# AUTH PAGE
 

def page_auth():
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 1.5rem;">
      <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:1.25rem;">
        <div style="width:40px;height:40px;background:#047857;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:18px;">📈</div>
        <span style="font-size:1.4rem;font-weight:700;color:#047857;">CryptoPortfolio</span>
      </div>
      <h1 style="font-size:1.6rem;font-weight:700;color:#047857;margin:0;">Welcome back</h1>
      <p style="color:#64748B;margin:.4rem 0 0;">Sign in to your investment dashboard</p>
    </div>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        t_in, t_reg = st.tabs(["Sign In", "Create Account"])
        with t_in:
            email = st.text_input("Email", key="li_e", placeholder="you@example.com")
            pwd   = st.text_input("Password", type="password", key="li_p",
                                  placeholder="Enter your password")
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not (email and pwd):
                    st.warning("Please fill in all fields.")
                elif (user := db.login_user(email, pwd)):
                    st.session_state.update(logged_in=True, user=user)
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        with t_reg:
            re = st.text_input("Email", key="re_e", placeholder="you@example.com")
            rp = st.text_input("Password", type="password", key="re_p",
                               placeholder="Minimum 6 characters")
            r2 = st.text_input("Confirm password", type="password", key="re_p2",
                               placeholder="Repeat your password")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not (re and rp and r2):
                    st.warning("Please fill in all fields.")
                elif rp != r2:
                    st.error("Passwords do not match.")
                elif len(rp) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    ok, msg = db.register_user(re, rp)
                    st.success(msg + " Please sign in.") if ok else st.error(msg)


 
# SIDEBAR
 

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:.75rem .5rem 1rem;border-bottom:1px solid rgba(255,255,255,.06);
                    margin-bottom:1rem;">
          <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:30px;height:30px;background:#047857;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;font-size:14px;">📈</div>
            <div>
              <div style="font-weight:700;color:#F1F5F9;font-size:.9rem;">CryptoPortfolio</div>
              <div style="font-size:.65rem;color:rgba(241,245,249,.35);">Investment Manager</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        has_key = bool(api_key())
        label   = "🟢 Sync Live Prices" if has_key else "⚪ No API Key Set"
        if st.button(label, use_container_width=True, disabled=not has_key):
            with st.spinner("Fetching live prices from CoinGecko…"):
                ok = sync_live_prices()
            if ok:
                st.success("Live prices updated!")
        if not has_key:
            st.caption("Set COINGECKO_API_KEY in your .env file.")

        st.markdown("<p style='color:rgba(241,245,249,.35);font-size:.65rem;font-weight:700;"
                    "letter-spacing:.08em;text-transform:uppercase;margin:1rem 0 .4rem .25rem;'>"
                    "Navigation</p>", unsafe_allow_html=True)

        for icon, pg in [("📊","Dashboard"),("📈","Market Analysis"),
                         ("🤖","AI Prediction"),("⚙️","Settings")]:
            if st.button(f"{icon}  {pg}", key=f"nav_{pg}", use_container_width=True,
                         type="primary" if st.session_state.page == pg else "secondary"):
                st.session_state.page = pg
                st.rerun()

        st.markdown("<br><div style='border-top:1px solid rgba(255,255,255,.05);'></div><br>",
                    unsafe_allow_html=True)
        email_addr = (st.session_state.user or {}).get("email", "")
        st.markdown(f"<div style='font-size:.75rem;color:rgba(203,213,225,.4);'>Signed in as</div>"
                    f"<div style='font-size:.8rem;color:rgba(203,213,225,.7);font-weight:500;"
                    f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{email_addr}</div>",
                    unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.update(logged_in=False, user=None,
                                    page="Dashboard", live_prices={})
            st.rerun()


 
# DASHBOARD PAGE
 

def page_dashboard():
    uid = st.session_state.user["id"]
    key = api_key()
    section_header("Dashboard", "Portfolio overview · P&L · Investment progress")

    if not key:
        st.warning("No API key detected. Set COINGECKO_API_KEY in your .env file.")

    if key:
        try:
            gl = fetch_global(key)
            if gl:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Market Cap",    f"${gl.get('total_market_cap',0)/1e12:.2f}T",
                                           f"{gl.get('market_cap_change',0):+.1f}% 24h")
                c2.metric("24h Volume",    f"${gl.get('total_volume',0)/1e9:.1f}B")
                c3.metric("BTC Dominance", f"{gl.get('btc_dominance',0):.1f}%")
                c4.metric("Active Coins",  f"{gl.get('active_coins',0):,}")
                st.markdown("---")
        except Exception as e:
            st.error(f"Failed to fetch global market data: {str(e)}")

    with st.expander("Add New Investment", expanded=False):
        st.info("Strategy: Conservative = 70% BTC/ETH · Balanced = 50/50 · Aggressive = 70% Altcoins")
        if not st.session_state.live_prices:
            st.warning("Live prices not loaded. Click Sync Live Prices in the sidebar first.")

        c1, c2 = st.columns(2)
        with c1:
            ids    = list(COINS.keys())
            labels = [f"{COINS[c]} ({c.upper()[:5]})" for c in ids]
            idx    = st.selectbox("Asset", range(len(ids)),
                                  format_func=lambda i: labels[i], key="add_ai")
            coin   = ids[idx]
            lp     = live_price(coin)
            st.caption(f"Live price: **{fmt(lp)}**" if lp > 0 else "Not yet loaded — sync first.")
        with c2:
            capital = st.number_input("Capital (USD)", min_value=1.0,
                                      value=1000.0, step=10.0, key="add_cap")

        st.markdown("**Strategy:**")
        ca, cb, cc = st.columns(3)
        strat = None
        with ca:
            if st.button("🛡 Conservative", use_container_width=True): strat = "conservative"
        with cb:
            if st.button("⚖ Balanced",     use_container_width=True): strat = "balanced"
        with cc:
            if st.button("🚀 Aggressive",   use_container_width=True): strat = "aggressive"

        if strat:
            if lp <= 0:
                st.error("Cannot add investment: live price unavailable. Please sync prices first.")
            else:
                db.add_holding(uid, coin, COINS[coin], round(capital / lp, 6), lp)
                st.success(f"Added {capital/lp:.5f} {COINS[coin]} @ {fmt(lp)} — {strat.title()}")
                st.rerun()

    holdings = db.get_holdings(uid)
    if not holdings:
        st.markdown("""
        <div style="text-align:center;padding:3rem;background:#fff;
                    border:1px solid #E2E8F0;border-radius:14px;">
          <div style="font-size:2.5rem;">🪙</div>
          <div style="font-weight:600;color:#0F172A;margin:.5rem 0 .25rem;">No investments yet</div>
          <div style="color:#64748B;font-size:.875rem;">Open "Add New Investment" to get started</div>
        </div>""", unsafe_allow_html=True)
        return

    if key:
        try:
            fresh = fetch_prices_bulk([h["coin_id"] for h in holdings], key)
            if fresh:
                st.session_state.live_prices.update(fresh)
            else:
                st.warning("Could not refresh live prices. Displaying last known values.")
        except Exception as e:
            st.error(f"Error fetching live prices: {str(e)}")

    if not st.session_state.live_prices:
        st.error("No live price data available. Click Sync Live Prices in the sidebar.")
        return

    rows, total_val, total_cost = compute_portfolio_rows(holdings)
    total_pl  = total_val - total_cost
    total_roi = (total_pl / total_cost * 100) if total_cost > 0 else 0
    best      = max(rows, key=lambda r: r["roi"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Portfolio Value",  f"${total_val:,.2f}",
                                  f"{'+' if total_roi>=0 else ''}{total_roi:.2f}%")
    m2.metric("Total Invested",   f"${total_cost:,.2f}")
    m3.metric("Total P&L",        f"{'+'if total_pl>=0 else ''}{fmt(abs(total_pl))[1:]}",
                                  "Profit" if total_pl >= 0 else "Loss",
                                  delta_color="normal" if total_pl >= 0 else "inverse")
    m4.metric("Best Performer",   best["coin_name"],
                                  f"{'+' if best['roi']>=0 else ''}{best['roi']:.2f}%")

    col_pie, col_tbl = st.columns([1, 2])
    with col_pie:
        df_pie = pd.DataFrame([{"Asset": r["coin_name"], "Value": r["live_value"]}
                                for r in rows])
        fig = px.pie(df_pie, values="Value", names="Asset",
                     hole=0.44, color_discrete_sequence=PALETTE)
        fig.update_layout(**chart_layout(height=300, showlegend=True,
                                         legend=dict(font=dict(size=11), orientation="v")))
        fig.update_layout(margin=dict(t=16, b=16, l=8, r=8))   
        fig.update_traces(textinfo="percent+label", textfont_size=11,
                          marker=dict(line=dict(color="#fff", width=2)))
        st.plotly_chart(fig, use_container_width=True)

    with col_tbl:
        st.markdown("""<div style="background:#F8FAFC;border:1px solid #E2E8F0;
            border-radius:10px 10px 0 0;">
          <table style="width:100%;border-collapse:collapse;font-size:.75rem;color:#64748B;">
            <tr>
              <th style="padding:10px 14px;text-align:left;font-weight:700;letter-spacing:.05em;text-transform:uppercase;">Asset</th>
              <th style="padding:10px 12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;">Qty / Buy</th>
              <th style="padding:10px 12px;text-align:right;font-weight:700;letter-spacing:.05em;text-transform:uppercase;">Value</th>
              <th style="padding:10px 12px;text-align:center;font-weight:700;letter-spacing:.05em;text-transform:uppercase;">ROI</th>
              <th style="padding:10px 12px;text-align:right;font-weight:700;letter-spacing:.05em;text-transform:uppercase;">P&amp;L</th>
              <th style="padding:10px 10px;"></th>
            </tr>
          </table></div>""", unsafe_allow_html=True)

        for r in rows:
            sign = "+" if r["pl"] >= 0 else ""
            c1, c2, c3, c4, c5, c6 = st.columns([2.2, 2.8, 1.8, 1.8, 1.8, 0.7])
            c1.markdown(f"**{r['coin_name']}**\n\n"
                        f"<span style='color:#94A3B8;font-size:.72rem;'>{r['coin_id'].upper()}</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"<span style='color:#64748B;font-size:.8rem;'>"
                        f"{r['quantity']:.4f} @ {fmt(r['purchase_price'])}</span>",
                        unsafe_allow_html=True)
            c3.markdown(f"<b>{fmt(r['live_value'])}</b>", unsafe_allow_html=True)
            c4.markdown(badge(r["roi"]), unsafe_allow_html=True)
            c5.markdown(f"<span style='color:{G if r['pl']>=0 else R};font-weight:600;'>"
                        f"{sign}{fmt(abs(r['pl']))[1:]}</span>", unsafe_allow_html=True)
            if c6.button("X", key=f"del_{r['id']}", help=f"Remove {r['coin_name']}"):
                db.delete_holding(r["id"]); st.rerun()

    st.markdown("---")
    st.markdown("### Investment Progress")
    st.caption("30-day price trend for each holding — live data from CoinGecko")

    cols = st.columns(min(len(rows), 3))
    for idx, r in enumerate(rows):
        with cols[idx % 3]:
            hist = []
            if key:
                try:
                    raw  = fetch_history(r["coin_id"], key, days=30)
                    hist = [p[1] for p in raw] if raw else []
                except Exception:
                    pass 

            if not hist:
                st.markdown(
                    f"<div style='background:#fff;border:1px solid #E2E8F0;border-radius:12px;"
                    f"padding:.75rem 1rem;margin-bottom:.5rem;'>"
                    f"<b style='font-size:.9rem;color:#0F172A;'>{r['coin_name']}</b><br>"
                    f"<span style='font-size:.78rem;color:#94A3B8;'>"
                    f"Trend data unavailable — check API limits</span></div>",
                    unsafe_allow_html=True)
                continue

            is_up     = hist[-1] >= hist[0]
            tc        = G if is_up else R
            trend_pct = ((hist[-1] - hist[0]) / hist[0] * 100) if hist[0] else 0

            fig = go.Figure(go.Scatter(
                y=hist, mode="lines",
                line=dict(color=tc, width=2),
                fill="tozeroy",
                fillcolor=f"rgba({'22,163,74' if is_up else '220,38,38'},.06)",
            ))
            fig.update_layout(height=80, margin=dict(t=4, b=4, l=4, r=4),
                              paper_bgcolor="#fff", plot_bgcolor="#fff",
                              xaxis=dict(visible=False), yaxis=dict(visible=False),
                              showlegend=False)

            st.markdown(
                f"<div style='background:#fff;border:1px solid #E2E8F0;border-radius:12px;"
                f"padding:.75rem 1rem .25rem;margin-bottom:.5rem;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
                f"<b style='font-size:.9rem;color:#0F172A;'>{r['coin_name']}</b>"
                f"<span style='color:{tc};font-size:.8rem;font-weight:600;'>"
                f"{'📈' if is_up else '📉'} {'+' if trend_pct>=0 else ''}{trend_pct:.1f}% 30d</span></div>"
                f"<div style='font-size:.78rem;color:#64748B;margin-top:.15rem;'>"
                f"Live: <b style='color:#0F172A;'>{fmt(r['live_price'])}</b> &nbsp;"
                f"P&L: <b style='color:{G if r['pl']>=0 else R};'>"
                f"{'+'if r['pl']>=0 else ''}{fmt(abs(r['pl']))[1:]}</b></div></div>",
                unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, key=f"sp_{r['id']}")

    st.markdown("---")
    ca, cb = st.columns([2, 1])
    cb.metric("Total Portfolio Value", f"${total_val:,.2f}",
                                       f"{'+'if total_pl>=0 else ''}{fmt(abs(total_pl))[1:]} P&L")
    buf = io.StringIO()
    pd.DataFrame([{
        "Asset": r["coin_name"], "Symbol": r["coin_id"].upper(),
        "Qty": r["quantity"], "Buy Price": r["purchase_price"],
        "Live Price": r["live_price"], "Live Value": round(r["live_value"], 2),
        "P&L": round(r["pl"], 2), "ROI%": round(r["roi"], 2),
    } for r in rows]).to_csv(buf, index=False)
    ca.download_button("Export Portfolio CSV", data=buf.getvalue(),
                       file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                       mime="text/csv")


 
# MARKET ANALYSIS PAGE
 

def page_market():
    key = api_key()
    section_header("Market Analysis", "Live global cryptocurrency data from CoinGecko")

    if not key:
        st.error("No API key configured. Set COINGECKO_API_KEY in your .env file.")
        return

    with st.spinner("Fetching global market data…"):
        try:
            gl = fetch_global(key)
        except Exception as e:
            st.error(f"Error connecting to CoinGecko: {str(e)}")
            gl = None

    if gl:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Market Cap",    f"${gl.get('total_market_cap',0)/1e12:.2f}T",
                                   f"{gl.get('market_cap_change',0):+.1f}%")
        c2.metric("24h Volume",    f"${gl.get('total_volume',0)/1e9:.1f}B")
        c3.metric("BTC Dominance", f"{gl.get('btc_dominance',0):.1f}%")
        c4.metric("Active Coins",  f"{gl.get('active_coins',0):,}")

    with st.spinner("Fetching live coin data…"):
        try:
            coins = fetch_markets(key, limit=25)
        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
            coins = None

    if not coins:
        st.warning("Failed to fetch market data. Check your API key and network connection.")
        return

    st.markdown("<div style='display:flex;align-items:center;justify-content:space-between;"
                "margin:.75rem 0;'><b style='font-size:.9375rem;color:#0F172A;'>Top 25 by Market Cap</b>"
                "<span style='background:#ECFDF5;color:#065F46;font-size:.75rem;font-weight:600;"
                "padding:3px 10px;border-radius:9999px;border:1px solid rgba(5,150,105,.2);'>"
                "Live</span></div>", unsafe_allow_html=True)

    def chg_badge(v: float) -> str:
        bg = "#ECFDF5" if v >= 0 else "#FEF2F2"
        fc = "#065F46" if v >= 0 else "#7F1D1D"
        ar = "▲" if v >= 0 else "▼"
        return (f"<span style='background:{bg};color:{fc};font-size:.78rem;"
                f"font-weight:600;padding:2px 8px;border-radius:9999px;'>"
                f"{ar} {abs(v):.2f}%</span>")

    rows_html = ""
    for i, c in enumerate(coins):
        p, chg24, chg7d = (c.get(k, 0) or 0 for k in ("price","change_24h","change_7d"))
        mc,  vol         = (c.get(k, 0) or 0 for k in ("market_cap","volume_24h"))
        mc_s  = f"${mc/1e12:.2f}T"  if mc  > 1e12 else f"${mc/1e9:.1f}B"
        vol_s = f"${vol/1e9:.1f}B"  if vol > 1e9  else f"${vol/1e6:.0f}M"
        sym   = c.get("symbol", "")
        rows_html += (
            f"<tr style='border-bottom:1px solid #F1F5F9;'>"
            f"<td style='padding:10px 14px;color:#94A3B8;font-size:.8rem;'>{i+1}</td>"
            f"<td style='padding:10px 14px;'><div style='display:flex;align-items:center;gap:10px;'>"
            f"<div style='width:32px;height:32px;border-radius:8px;background:#ECFDF5;"
            f"display:flex;align-items:center;justify-content:center;"
            f"font-size:.65rem;font-weight:700;color:#047857;'>{sym[:4]}</div>"
            f"<div><div style='font-weight:600;font-size:.9rem;color:#0F172A;'>{c.get('name','')}</div>"
            f"<div style='font-size:.72rem;color:#94A3B8;'>{sym.upper()}</div></div>"
            f"</div></td>"
            f"<td style='padding:10px 14px;font-weight:600;color:#0F172A;'>{fmt(p)}</td>"
            f"<td style='padding:10px 14px;color:#64748B;'>{mc_s}</td>"
            f"<td style='padding:10px 14px;color:#64748B;'>{vol_s}</td>"
            f"<td style='padding:10px 14px;'>{chg_badge(chg24)}</td>"
            f"<td style='padding:10px 14px;'>{chg_badge(chg7d)}</td></tr>"
        )

    hdrs = ["#","Asset","Price","Market Cap","Vol 24h","24h","7d"]
    hcells = "".join(f'<th style="padding:10px 14px;text-align:left;font-size:.68rem;'
                     f'font-weight:700;letter-spacing:.06em;text-transform:uppercase;'
                     f'color:#64748B;">{h}</th>' for h in hdrs)
    st.markdown(
        f"<div style='background:#fff;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;'>"
        f"<table style='width:100%;border-collapse:collapse;'>"
        f"<thead><tr style='background:#F8FAFC;border-bottom:1px solid #E2E8F0;'>"
        f"{hcells}</tr></thead><tbody>{rows_html}</tbody></table></div>",
        unsafe_allow_html=True)


 
# AI PREDICTION PAGE
 

def page_ai():
    key = api_key()
    section_header("AI Price Predictor", "7-day forecast · Scikit-Learn Linear Regression")

    if not key:
        st.error("No API key configured. Set COINGECKO_API_KEY in your .env file.")
        return

    ids    = list(COINS.keys())
    labels = [f"{COINS[c]} ({c.upper()[:5]})" for c in ids]
    idx    = st.selectbox("Select Asset", range(len(ids)),
                          format_func=lambda i: labels[i], key="ai_sel")
    coin   = ids[idx]
    c1, _  = st.columns([1, 3])
    with c1:
        days = st.select_slider("Training period (days)",
                                [30, 60, 90, 180], value=90, key="ai_days")

    if not st.button("Generate Forecast", type="primary"):
        return

    with st.spinner("Fetching historical data from CoinGecko…"):
        try:
            pts = fetch_history(coin, key, days=days)
        except Exception as e:
            st.error(f"API Error fetching history: {str(e)}")
            pts = []

    if not pts or len(pts) < 7:
        st.error(
            "Not enough historical data from CoinGecko. "
            "Try a different coin or a shorter training period, "
            "or check your API key and rate limits."
        )
        return

    with st.spinner("Running Linear Regression model…"):
        dates, preds = predict_7days(pts)

    if not dates:
        st.error("Prediction failed — insufficient data points after processing.")
        return

    hist_prices = [p[1] for p in pts]
    trend = preds[-1] - preds[0]
    is_up = trend >= 0
    tc    = G if is_up else R

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(hist_prices))), y=hist_prices,
                             mode="lines", name="Historical",
                             line=dict(color=B, width=2.5),
                             fill="tozeroy", fillcolor="rgba(4,120,87,.06)"))
    fig.add_trace(go.Scatter(
        x=list(range(len(hist_prices), len(hist_prices) + 7)), y=preds,
        mode="lines+markers", name="Forecast",
        line=dict(color="#F59E0B", width=2.5, dash="dash"),
        marker=dict(color="#F59E0B", size=8, line=dict(color="#fff", width=2))))
    fig.update_layout(**chart_layout(
        height=420,
        title=dict(text=f"{COINS[coin]} — Historical + 7-Day AI Forecast",
                   font=dict(color="#0F172A", size=15)),
        xaxis=dict(title="Day"), yaxis=dict(title="Price (USD)"),
    ))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"<div style='margin:.5rem 0 1rem;display:flex;align-items:center;gap:10px;'>"
        f"<span style='font-size:1rem;font-weight:700;color:{tc};'>"
        f"{'📈 Upward' if is_up else '📉 Downward'} trend</span>"
        f"<span style='color:#64748B;font-size:.875rem;'>"
        f"{'+' if trend>=0 else ''}{fmt(abs(trend))[1:]} over 7 days</span></div>",
        unsafe_allow_html=True)

    st.markdown("##### 7-Day Forecast")
    day_cols = st.columns(7)
    for i, (d, p) in enumerate(zip(dates, preds)):
        prev   = preds[i-1] if i > 0 else hist_prices[-1]
        chg    = ((p - prev) / prev * 100) if prev > 0 else 0
        chg_c  = G if chg >= 0 else R
        chg_bg = "#ECFDF5" if chg >= 0 else "#FEF2F2"
        day_cols[i].markdown(
            f"<div style='background:#fff;border:1px solid #E2E8F0;border-radius:10px;"
            f"padding:.7rem .5rem;text-align:center;'>"
            f"<div style='font-size:.7rem;color:#64748B;font-weight:500;margin-bottom:.25rem;'>{d}</div>"
            f"<div style='font-size:.85rem;font-weight:700;color:#0F172A;margin-bottom:.25rem;'>{fmt(p)}</div>"
            f"<div style='background:{chg_bg};color:{chg_c};font-size:.68rem;font-weight:600;"
            f"padding:1px 7px;border-radius:9999px;'>{'+' if chg>=0 else ''}{chg:.1f}%</div></div>",
            unsafe_allow_html=True)


 
# SETTINGS PAGE
 

def _make_pdf(uid: int) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=.75*inch, rightMargin=.75*inch,
                            topMargin=.75*inch, bottomMargin=.75*inch)
    ss = getSampleStyleSheet()
    ts = ParagraphStyle("T", parent=ss["Title"], fontSize=20, textColor=rc.HexColor("#047857"))
    bs = ParagraphStyle("B", parent=ss["Normal"], fontSize=10, spaceAfter=6)
    hs = ParagraphStyle("H", parent=ss["Heading2"], fontSize=13, textColor=rc.HexColor("#0F172A"))
    ds = ParagraphStyle("D", parent=ss["Normal"], fontSize=8, textColor=rc.grey)

    story = [Paragraph("Crypto Portfolio Audit Report", ts),
             Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", bs),
             Spacer(1, .2*inch), Paragraph("Holdings", hs)]

    holdings = db.get_holdings(uid)
    if holdings:
        data = [["Asset","Qty","Buy","Live","Value","P&L","ROI%"]]
        tv, tp = 0.0, 0.0
        for h in holdings:
            lp  = live_price(h["coin_id"])
            val = h["quantity"] * lp
            pl  = val - h["quantity"] * h["purchase_price"]
            roi = ((lp - h["purchase_price"]) / h["purchase_price"] * 100
                   if h["purchase_price"] else 0)
            tv += val; tp += pl
            data.append([h["coin_name"], f"{h['quantity']:.5f}",
                         f"${h['purchase_price']:,.4g}", f"${lp:,.4g}",
                         f"${val:,.2f}", f"${pl:+,.2f}", f"{roi:+.2f}%"])
        data.append(["TOTAL","","","",f"${tv:,.2f}",f"${tp:+,.2f}",""])
        tbl = Table(data, colWidths=[1.2*inch,.85*inch,.9*inch,.9*inch,.9*inch,.9*inch,.75*inch])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),rc.HexColor("#047857")),
            ("TEXTCOLOR",(0,0),(-1,0),rc.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("ALIGN",(1,0),(-1,-1),"RIGHT"), ("ALIGN",(0,0),(0,-1),"LEFT"),
            ("ROWBACKGROUNDS",(0,1),(-1,-2),[rc.HexColor("#ECFDF5"),rc.white]),
            ("BACKGROUND",(0,-1),(-1,-1),rc.HexColor("#D1FAE5")),
            ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),.3,rc.HexColor("#E2E8F0")),
            ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph("No holdings found.", bs))

    story += [Spacer(1,.3*inch), Paragraph("Disclaimer", hs),
              Paragraph("For informational purposes only. Not financial advice.", ds)]
    doc.build(story)
    return buf.getvalue()


def page_settings():
    uid      = st.session_state.user["id"]
    settings = db.get_settings(uid)
    section_header("Settings", "Alerts · Reports · Diversification")

    t_alert, t_report, t_div = st.tabs(["🔔 Alerts", "📄 Reports", "🎯 Diversification"])

    with t_alert:
        st.markdown("### Risk Alert Threshold")
        thr = st.slider("Alert when asset drops by (%)", 1., 50.,
                        float(settings.get("risk_threshold", 10.)), 0.5, key="thr")
        st.markdown("### Email Alert Configuration")
        st.caption("Gmail: generate an App Password at myaccount.google.com/apppasswords")
        email = st.text_input("Recipient email", value=settings.get("alert_email",""),
                              placeholder="you@example.com")
        shost = st.text_input("SMTP Host", value="smtp.gmail.com")
        suser = st.text_input("SMTP Username", placeholder="sender@gmail.com")
        spass = st.text_input("SMTP Password", type="password",
                              placeholder="App password (not account password)")

        if st.button("Save Alert Settings", type="primary"):
            db.save_settings(uid, thr, email)
            st.success(f"Saved — threshold {thr:.1f}%, alerts to {email or 'not set'}")

        st.markdown("---")
        if st.button("Send Test Alert"):
            if email and suser and spass:
                ok, msg = send_alert(email,"bitcoin",-15.5,73632,shost,587,suser,spass)
                st.success(msg) if ok else st.error(msg)
            else:
                st.warning("Fill in email and SMTP credentials first.")

        st.markdown("---")
        st.markdown("### Live Alert Status")
        holdings = db.get_holdings(uid)
        if holdings:
            triggered = False
            for h in holdings:
                lp = live_price(h["coin_id"])
                if lp > 0 and h["purchase_price"] > 0:
                    chg = (lp - h["purchase_price"]) / h["purchase_price"] * 100
                    if abs(chg) >= thr:
                        triggered = True
                        st.warning(f"⚠ **{h['coin_name']}** has "
                                   f"{'dropped' if chg<0 else 'risen'} {abs(chg):.1f}%")
            if not triggered:
                st.success(f"All holdings within {thr:.1f}% threshold")
        else:
            st.info("Add holdings in the Dashboard to monitor alerts.")

    with t_report:
        st.markdown("### Portfolio Audit Report")
        st.info("Download a PDF or CSV with live valuations and P&L.")
        ca, cb = st.columns(2)
        with ca:
            if st.button("Generate PDF", type="primary", use_container_width=True):
                if db.get_holdings(uid):
                    st.download_button("Download PDF", data=_make_pdf(uid),
                                       file_name=f"audit_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                       mime="application/pdf", use_container_width=True)
                else:
                    st.warning("Add holdings first.")
        with cb:
            if st.button("Export CSV", use_container_width=True):
                h_list = db.get_holdings(uid)
                if h_list:
                    rows, *_ = compute_portfolio_rows(h_list)
                    buf = io.StringIO()
                    pd.DataFrame([{
                        "Asset": r["coin_name"], "Symbol": r["coin_id"].upper(),
                        "Qty": r["quantity"], "Buy": r["purchase_price"],
                        "Live": r["live_price"], "Value": round(r["live_value"],2),
                        "P&L": round(r["pl"],2), "ROI%": round(r["roi"],2),
                    } for r in rows]).to_csv(buf, index=False)
                    st.download_button("Download CSV", data=buf.getvalue(),
                                       file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                                       mime="text/csv", use_container_width=True)
                else:
                    st.warning("No holdings to export.")

    with t_div:
        st.markdown("### Diversification Rules")
        st.caption("Recommended allocation splits for your current holdings.")
        holdings = db.get_holdings(uid)
        if not holdings:
            st.info("Add holdings in the Dashboard first.")
            return
        portfolio = {h["coin_id"]: 1 for h in holdings}
        for label, strat in [("🛡 Conservative","conservative"),
                              ("⚖ Balanced","balanced"),
                              ("🚀 Aggressive","aggressive")]:
            if st.button(label, key=f"div_{strat}", use_container_width=True):
                alloc = apply_diversification_rules(portfolio, strat)
                st.markdown(f"**{strat.title()} allocation:**")
                for cid, pct in alloc.items():
                    st.markdown(
                        f"<div style='display:flex;align-items:center;gap:8px;margin:.3rem 0;'>"
                        f"<span style='width:90px;font-size:.8rem;font-weight:500;color:#0F172A;'>"
                        f"{COINS.get(cid,cid)}</span>"
                        f"<div style='flex:1;height:6px;background:#E2E8F0;border-radius:9999px;overflow:hidden;'>"
                        f"<div style='width:{pct:.0f}%;height:100%;background:#047857;border-radius:9999px;'>"
                        f"</div></div>"
                        f"<span style='width:40px;text-align:right;font-size:.8rem;"
                        f"font-weight:600;color:#047857;'>{pct:.1f}%</span></div>",
                        unsafe_allow_html=True)


 
# MAIN ROUTER
 

def main():
    if not st.session_state.logged_in:
        page_auth()
        return
    render_sidebar()
    page = st.session_state.page
    if   page == "Dashboard":       page_dashboard()
    elif page == "Market Analysis": page_market()
    elif page == "AI Prediction":   page_ai()
    elif page == "Settings":        page_settings()


if __name__ == "__main__":
    main()