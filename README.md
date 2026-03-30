# 🪙 Crypto Portfolio Manager

A full-featured Python crypto investment management system built with Streamlit, Scikit-Learn, SQLite, Plotly, and ReportLab.

---

## 📦 Features

| Module | Description |
|--------|-------------|
| **Dashboard** | Add investments, view pie chart allocation, live ROI, delete holdings, export CSV |
| **Market Analysis** | Live global market tracker with price + market cap data |
| **Risk & Volatility** | Parallel risk analysis, volatility bar chart, global risk gauge (0–10), alert thresholds |
| **AI Prediction** | 7-day ML forecast using Scikit-Learn Linear Regression with historical + predicted chart |
| **Settings** | Risk threshold slider, PDF audit report generation, email alert config, diversification rules |

---

## 🚀 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 📁 Project Structure

```
crypto-portfolio-manager/
├── app.py                      # Main Streamlit application
├── database_manager.py         # SQLite DB: users, holdings, price trends, settings
├── predictor.py                # AI/ML: Scikit-Learn 7-day price prediction
├── notifications.py            # Email alert service (SMTP)
├── styles.py                   # CSS theming & UI helpers
├── requirements.txt
├── core/
│   ├── __init__.py
│   └── risk_engine.py          # Risk calc: volatility, Sharpe, diversification rules
└── data/
    └── historical_prices.csv   # 30-day historical prices for 12 cryptocurrencies
```

---

## 🏗️ Architecture & Modules

### Module 1: Investment Mix Calculator (`app.py` → Dashboard)
- Rule-based diversification: Conservative (70% BTC/ETH), Balanced (50/50), Aggressive (70% Altcoins)
- Capital allocation computed in real-time
- Parallel price syncing via `ThreadPoolExecutor`

### Module 2: Risk Checker & Predictor (`core/risk_engine.py`, `predictor.py`)
- Annualised volatility = `std(log_returns) × √365`
- Parallel risk analysis across all 12 coins via `ThreadPoolExecutor`
- Linear Regression trained on date ordinals vs price
- Risk stored in SQLite `price_trends` table

### Module 3: Report & File Saver (`app.py` → Risk & Volatility / Dashboard)
- CSV export of full portfolio with ROI
- PDF Audit Report via ReportLab (holdings table + risk score)
- Email alerts via SMTP (configurable)

### Module 4: Spreading Rule Setter (`core/risk_engine.py`)
- `apply_diversification_rules(portfolio, strategy)` → allocation percentages
- Three strategies tested in Settings page

---

## 🗄️ Database Schema (SQLite)

```sql
users          (id, email, password_hash, created)
holdings       (id, user_id, coin_id, quantity, purchase_price, added_at)
price_trends   (id, coin_id, price, recorded)
settings       (user_id, risk_threshold, alert_email)
```

---

## 📊 Milestones Implemented

| Milestone | Status | Features |
|-----------|--------|---------|
| Week 1-2: Setup | ✅ | SQLite DB, parallel tasks, data structure |
| Week 3-4: Mix Calculator | ✅ | Dashboard, strategy allocation, CSV export |
| Week 5-6: Risk & Reports | ✅ | Volatility analysis, PDF reports, email alerts |
| Week 7-8: Rule Setter | ✅ | Diversification rules, multi-scenario testing |

---

## ⚙️ Configuration

To enable real email alerts, configure in Settings:
- **SMTP Host**: e.g. `smtp.gmail.com`
- **SMTP Username**: your Gmail address
- **SMTP Password**: your app password (not account password)
- **Alert Email**: recipient address

> ⚠️ For Gmail, enable 2FA and create an App Password at myaccount.google.com/apppasswords

---

## 📈 Sample Users for Testing

Register any email/password via the app's Register tab.
All data is stored locally in `data/crypto_portfolio.db`.
