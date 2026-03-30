# Agile Project Documentation: CryptoPortfolio Manager

## 🎯 Project Vision
To build a secure, full-stack cryptocurrency portfolio management dashboard that allows users to track live asset values, analyze global market trends, and utilize Machine Learning to forecast short-term price movements.

## 👥 User Personas
1. **The Casual Investor:** Wants a clean, simple dashboard to see if their holdings are in profit or loss without dealing with complex exchange interfaces.
2. **The Data-Driven Trader:** Wants historical trendlines, AI-driven price predictions, and automated risk-management alerts.

---

## 📦 Epics & User Stories

### Epic 1: Secure Authentication & State Management
* **User Story 1.1:** As a user, I want to create an account and log in securely so that my financial data remains private.
  * *Acceptance Criteria:* Passwords must be hashed/secure. Sessions must persist during navigation. UI must block unauthorized access.
* **User Story 1.2:** As a developer, I need to securely manage API keys so that sensitive credentials are not exposed in the source code.
  * *Acceptance Criteria:* Implement `.env` integration and `.gitignore` protocols.

### Epic 2: Real-Time Market Integration
* **User Story 2.1:** As an investor, I want to see real-time, accurate cryptocurrency prices so I can track my true portfolio value.
  * *Acceptance Criteria:* Integrate CoinGecko API. Implement a caching layer to prevent API rate-limiting.
* **User Story 2.2:** As a trader, I want to view the top 25 global coins by market cap to identify market trends.
  * *Acceptance Criteria:* Fetch market data and render it in a sortable, color-coded HTML data table.

### Epic 3: Portfolio Analytics & Dashboard
* **User Story 3.1:** As an investor, I want to simulate buying assets and immediately see my exact Return on Investment (ROI) and Profit/Loss (P&L).
  * *Acceptance Criteria:* Build a robust math engine to merge database holdings with live API prices.
* **User Story 3.2:** As a visual learner, I want to see a breakdown of my asset allocation so I understand my exposure.
  * *Acceptance Criteria:* Render a dynamic, interactive donut chart using Plotly/Pandas.

### Epic 4: Machine Learning & Forecasting
* **User Story 4.1:** As a data-driven trader, I want to see a 7-day price forecast based on recent historical data so I can plan my entry/exit strategies.
  * *Acceptance Criteria:* Implement a Scikit-Learn Linear Regression model. Fetch 90 days of time-series data, train the model, and plot the 7-day extrapolation against the historical baseline.

### Epic 5: Risk Management & Reporting
* **User Story 5.1:** As a risk-averse investor, I want to receive an automated email if any of my assets drop below a specific percentage threshold.
  * *Acceptance Criteria:* Integrate Python SMTP library. Allow users to configure their risk threshold and email preferences via a Settings UI.
* **User Story 5.2:** As a user, I want to export my live portfolio data for tax or record-keeping purposes.
  * *Acceptance Criteria:* Generate downloadable CSV spreadsheets and formatted PDF audit reports using in-memory byte streams.

---

## 🏃‍♂️ Sprint History

### Sprint 1: Architecture & Foundation
* Set up global CSS design tokens and Plotly layout templates.
* Built the SQLite database schema (`database_manager.py`).
* Implemented user registration, login, and session state caching.

### Sprint 2: The Data Pipeline
* Built `coingecko_api.py` with strict `try/except` error handling.
* Implemented a custom timestamp-based caching dictionary to respect API rate limits.
* Built the bulk-fetch functions to pull live portfolio prices efficiently.

### Sprint 3: UI & Analytics Engine
* Engineered `compute_portfolio_rows()` to calculate complex P&L and ROI math.
* Constructed the main interactive Dashboard view.
* Built the Global Market Analysis data table with dynamic conditional formatting.

### Sprint 4: Advanced Features & Deployment
* Isolated the Machine Learning logic into `predictor.py`.
* Engineered the PDF generation (`ReportLab`) and CSV export (`Pandas`) features.
* Built `notifications.py` for automated SMTP alerts.
* Finalized Agile documentation and repository structure.

---
*Document maintained by Shannu Pippalla.*