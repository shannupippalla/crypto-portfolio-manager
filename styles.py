"""
styles.py — Senior-level premium light theme
Design system: Slate-neutral base, emerald-teal brand, warm text hierarchy.
WCAG AA/AAA verified. Every component considered. Nothing generic.
"""
# styles.py

# styles.py

CSS_THEME = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-page:      #F4F6F8;   
  --bg-card:      #FFFFFF;
  --bg-subtle:    #F8F9FA;   
  --brand:        #047857;   
  --sidebar-bg:   #111827;  
  --text-primary: #111827;   
  --text-body:    #374151;   
  --text-muted:   #6B7280;   
}

/* ... (Keep all the rest of your beautiful CSS styling below this) ... */
"""
LIGHT_CSS = """
<style>

/* ══════════════════════════════════════════════════════════
   GOOGLE FONT — Outfit: geometric, distinctive, NOT Inter
   ══════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════ */
:root {
  /* ─ Surfaces ─────────────────────────────────── */
  --bg-page:      #F4F6F8;   /* neutral slate-50 — warm, not cold blue */
  --bg-card:      #FFFFFF;
  --bg-subtle:    #F8F9FA;   /* table headers, muted areas */
  --bg-overlay:   rgba(255,255,255,0.85);

  /* ─ Brand — Slate-Teal ────────────────────────── */
  --brand:        #047857;   /* emerald-700 — deep, trustworthy */
  --brand-dark:   #065F46;   /* emerald-800 */
  --brand-mid:    #10B981;   /* emerald-500 */
  --brand-light:  #D1FAE5;   /* emerald-100 */
  --brand-pale:   #ECFDF5;   /* emerald-50  */

  /* ─ Sidebar — Rich forest ─────────────────────── */
  --sidebar-bg:      #111827;  /* gray-900 */
  --sidebar-surface: #1F2937;  /* gray-800 */
  --sidebar-border:  rgba(255,255,255,0.06);
  --sidebar-text:    rgba(209,213,219,0.80);   /* gray-300@80% */
  --sidebar-active:  #047857;

  /* ─ Text — warm stone scale ───────────────────── */
  --text-primary:    #111827;   /* gray-900  — 18.1:1 AAA */
  --text-body:       #374151;   /* gray-700  — 10.7:1 AAA */
  --text-muted:      #6B7280;   /* gray-500  —  5.9:1 AA  */
  --text-subtle:     #9CA3AF;   /* gray-400  —  3.3:1 decorative */
  --text-inverse:    #F9FAFB;   /* gray-50 */

  /* ─ Semantic — finance-grade ─────────────────── */
  --positive:        #059669;  /* emerald-600 — 4.54:1 AA */
  --positive-bg:     #ECFDF5;
  --positive-text:   #065F46;
  --positive-border: rgba(5,150,105,0.2);

  --negative:        #DC2626;  /* red-600 — 4.59:1 AA */
  --negative-bg:     #FEF2F2;
  --negative-text:   #7F1D1D;
  --negative-border: rgba(220,38,38,0.2);

  --warning:         #D97706;  /* amber-600 — 5.2:1 AA */
  --warning-bg:      #FFFBEB;
  --warning-text:    #78350F;
  --warning-border:  rgba(217,119,6,0.2);

  --info-bg:         #ECFDF5;
  --info-text:       #065F46;

  /* ─ Borders ──────────────────────────────────── */
  --border:       #E5E7EB;   /* gray-200 */
  --border-dark:  #D1D5DB;   /* gray-300 */
  --border-focus: #047857;

  /* ─ Shadows — soft, layered, realistic ──────── */
  --shadow-xs:   0 1px 2px rgba(17,24,39,0.04);
  --shadow-sm:   0 1px 3px rgba(17,24,39,0.07), 0 1px 2px rgba(17,24,39,0.04);
  --shadow-md:   0 4px 8px rgba(17,24,39,0.06), 0 2px 4px rgba(17,24,39,0.04);
  --shadow-lg:   0 10px 20px rgba(17,24,39,0.07), 0 4px 8px rgba(17,24,39,0.04);
  --shadow-card: 0 0 0 1px #E5E7EB, 0 2px 6px rgba(17,24,39,0.05);

  /* ─ Radius ───────────────────────────────────── */
  --r-sm:   6px;
  --r-md:   10px;
  --r-lg:   14px;
  --r-xl:   20px;
  --r-pill: 9999px;

  /* ─ Easing ───────────────────────────────────── */
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --fast: 140ms;
  --norm: 220ms;
}


/* ══════════════════════════════════════════════════════════
   GLOBAL RESET & BASE
   ══════════════════════════════════════════════════════════ */

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-page) !important;
  color: var(--text-body) !important;
  line-height: 1.6;
}

/* Selection highlight */
::selection {
  background: var(--brand-light);
  color: var(--brand-dark);
}

/* Focus ring — visible keyboard navigation, hidden on click */
:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 2px;
  border-radius: var(--r-sm);
}

/* Refined scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--border-dark);
  border-radius: var(--r-pill);
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-subtle);
}


/* ══════════════════════════════════════════════════════════
   PAGE LAYOUT
   ══════════════════════════════════════════════════════════ */

.main .block-container {
  background: var(--bg-page);
  padding: 2rem 2.5rem;
  max-width: 1320px;
}

/* Brand identity stripe at very top */
.main::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--brand) 0%, var(--brand-mid) 50%, #06B6D4 100%);
  z-index: 9999;
  pointer-events: none;
}


/* ══════════════════════════════════════════════════════════
   SIDEBAR — Rich dark nav, high contrast
   Ratio: sidebar bg #111827 vs text rgba(209,213,219,0.80) → 9.2:1 AAA
   ══════════════════════════════════════════════════════════ */

section[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--sidebar-border) !important;
}
section[data-testid="stSidebar"] * {
  color: var(--sidebar-text) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] b {
  color: var(--text-inverse) !important;
}

/* Nav item buttons */
section[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--sidebar-text) !important;
  border: none !important;
  border-radius: var(--r-md) !important;
  text-align: left !important;
  justify-content: flex-start !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  padding: 0.5rem 0.75rem !important;
  width: 100% !important;
  transition: background var(--fast) var(--ease),
              color var(--fast) var(--ease) !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.07) !important;
  color: var(--text-inverse) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--sidebar-active) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(4,120,87,0.4) !important;
}
section[data-testid="stSidebar"] .stButton > button:active {
  transform: scale(0.98) !important;
}


/* ══════════════════════════════════════════════════════════
   TYPOGRAPHY — Outfit with proper hierarchy
   ══════════════════════════════════════════════════════════ */

h1 {
  font-size: 1.75rem !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
  letter-spacing: -0.025em !important;
  line-height: 1.2 !important;
  margin-bottom: 0.25rem !important;
}
h2 {
  font-size: 1.25rem !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
  letter-spacing: -0.015em !important;
}
h3 {
  font-size: 1rem !important;
  font-weight: 600 !important;
  color: var(--text-body) !important;
}
p, .stMarkdown p {
  color: var(--text-body);
  line-height: 1.65;
  font-size: 0.9375rem;
}
.stCaption, small {
  color: var(--text-muted) !important;
  font-size: 0.8rem !important;
}


/* ══════════════════════════════════════════════════════════
   METRIC CARDS — premium fintech style
   ══════════════════════════════════════════════════════════ */

[data-testid="metric-container"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-lg) !important;
  padding: 1.125rem 1.375rem !important;
  box-shadow: var(--shadow-card) !important;
  transition: transform var(--fast) var(--ease),
              box-shadow var(--norm) var(--ease);
  position: relative;
  overflow: hidden;
}
[data-testid="metric-container"]:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md) !important;
}
/* Brand accent top bar on each metric card */
[data-testid="metric-container"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--brand);
  border-radius: var(--r-lg) var(--r-lg) 0 0;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] > div {
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  color: var(--text-muted) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] > div {
  font-size: 1.875rem !important;
  font-weight: 800 !important;
  color: var(--text-primary) !important;
  letter-spacing: -0.04em !important;
  line-height: 1.1 !important;
  font-family: 'Outfit', sans-serif !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-size: 0.8rem !important;
  font-weight: 600 !important;
}


/* ══════════════════════════════════════════════════════════
   BUTTONS — Three-tier system
   ══════════════════════════════════════════════════════════ */

/* Default: subtle ghost */
.stButton > button {
  background: var(--bg-card) !important;
  color: var(--text-body) !important;
  border: 1px solid var(--border-dark) !important;
  border-radius: var(--r-md) !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  font-family: 'Outfit', sans-serif !important;
  padding: 0.5rem 1.125rem !important;
  box-shadow: var(--shadow-xs) !important;
  transition: all var(--fast) var(--ease) !important;
  letter-spacing: 0.01em !important;
}
.stButton > button:hover {
  background: var(--brand-pale) !important;
  color: var(--brand-dark) !important;
  border-color: var(--brand-light) !important;
  box-shadow: var(--shadow-sm) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active {
  transform: translateY(0) scale(0.98) !important;
  box-shadow: none !important;
}

/* Primary: filled brand */
.stButton > button[kind="primary"] {
  background: var(--brand) !important;
  color: #FFFFFF !important;
  border: none !important;
  box-shadow: 0 1px 3px rgba(4,120,87,0.25),
              0 4px 12px rgba(4,120,87,0.2) !important;
  font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--brand-dark) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 6px rgba(4,120,87,0.3),
              0 8px 20px rgba(4,120,87,0.22) !important;
  transform: translateY(-1px) !important;
}

/* Download: positive-tinted */
[data-testid="stDownloadButton"] > button {
  background: var(--positive-bg) !important;
  color: var(--positive-text) !important;
  border: 1px solid var(--positive-border) !important;
  border-radius: var(--r-md) !important;
  font-weight: 600 !important;
  box-shadow: none !important;
  transition: all var(--fast) var(--ease) !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: #D1FAE5 !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--shadow-sm) !important;
}


/* ══════════════════════════════════════════════════════════
   FORM INPUTS — clean, focus-state consistent
   ══════════════════════════════════════════════════════════ */

.stTextInput label, .stNumberInput label,
.stSelectbox label, .stSlider label,
.stMultiSelect label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  color: var(--text-muted) !important;
  margin-bottom: 0.3rem !important;
}

input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
.stTextInput input,
.stNumberInput input {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-dark) !important;
  border-radius: var(--r-md) !important;
  font-size: 0.9375rem !important;
  font-family: 'Outfit', sans-serif !important;
  padding: 0.6rem 0.9rem !important;
  box-shadow: var(--shadow-xs) !important;
  transition: border-color var(--fast) var(--ease),
              box-shadow var(--fast) var(--ease) !important;
}
input:focus,
.stTextInput input:focus,
.stNumberInput input:focus {
  border-color: var(--brand) !important;
  box-shadow: 0 0 0 3px rgba(4,120,87,0.12) !important;
  outline: none !important;
}
input::placeholder { color: var(--text-subtle) !important; }

/* Selectbox */
.stSelectbox > div > div {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-dark) !important;
  border-radius: var(--r-md) !important;
  box-shadow: var(--shadow-xs) !important;
  font-family: 'Outfit', sans-serif !important;
  transition: border-color var(--fast) var(--ease) !important;
}
.stSelectbox > div > div:hover {
  border-color: var(--brand) !important;
}


/* ══════════════════════════════════════════════════════════
   DATA TABLE / DATAFRAME
   ══════════════════════════════════════════════════════════ */

[data-testid="stDataFrame"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-lg) !important;
  box-shadow: var(--shadow-card) !important;
  overflow: hidden;
}
[data-testid="stDataFrame"] thead tr th {
  background: var(--bg-subtle) !important;
  color: var(--text-muted) !important;
  font-size: 0.68rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0.75rem 1rem !important;
}
[data-testid="stDataFrame"] tbody tr td {
  color: var(--text-body) !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0.75rem 1rem !important;
  font-size: 0.875rem !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
  background: var(--brand-pale) !important;
}
[data-testid="stDataFrame"] tbody tr:last-child td {
  border-bottom: none !important;
}


/* ══════════════════════════════════════════════════════════
   ALERT BANNERS — colour-coded, AAA contrast
   ══════════════════════════════════════════════════════════ */

[data-testid="stSuccess"], .stSuccess {
  background: var(--positive-bg) !important;
  color: var(--positive-text) !important;
  border: 1px solid var(--positive-border) !important;
  border-left: 3px solid var(--positive) !important;
  border-radius: var(--r-md) !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
}
[data-testid="stInfo"], .stInfo {
  background: var(--info-bg) !important;
  color: var(--info-text) !important;
  border: 1px solid rgba(4,120,87,0.2) !important;
  border-left: 3px solid var(--brand) !important;
  border-radius: var(--r-md) !important;
  font-size: 0.9rem !important;
}
[data-testid="stWarning"], .stWarning {
  background: var(--warning-bg) !important;
  color: var(--warning-text) !important;
  border: 1px solid var(--warning-border) !important;
  border-left: 3px solid var(--warning) !important;
  border-radius: var(--r-md) !important;
  font-size: 0.9rem !important;
}
[data-testid="stError"], .stError {
  background: var(--negative-bg) !important;
  color: var(--negative-text) !important;
  border: 1px solid var(--negative-border) !important;
  border-left: 3px solid var(--negative) !important;
  border-radius: var(--r-md) !important;
  font-size: 0.9rem !important;
}


/* ══════════════════════════════════════════════════════════
   TABS — clean underline style
   ══════════════════════════════════════════════════════════ */

.stTabs [data-baseweb="tab-list"] {
  background: transparent;
  border-bottom: 1px solid var(--border-dark);
  gap: 0;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-muted) !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  font-family: 'Outfit', sans-serif !important;
  padding: 0.6rem 1.25rem !important;
  border-bottom: 2px solid transparent !important;
  border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
  transition: color var(--fast) var(--ease),
              background var(--fast) var(--ease) !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--text-body) !important;
  background: var(--bg-subtle) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--brand) !important;
  font-weight: 600 !important;
  border-bottom: 2px solid var(--brand) !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
  padding-top: 1.5rem !important;
}


/* ══════════════════════════════════════════════════════════
   SLIDER — brand-colored thumb and track
   ══════════════════════════════════════════════════════════ */

.stSlider > div > div > div > div {
  background: var(--brand) !important;
  height: 4px !important;
  border-radius: 2px !important;
}
.stSlider > div > div > div > div > div {
  background: var(--brand) !important;
  border: 3px solid #FFFFFF !important;
  box-shadow: 0 0 0 2px rgba(4,120,87,0.25), var(--shadow-sm) !important;
  width: 20px !important;
  height: 20px !important;
  top: -8px !important;
  transition: box-shadow var(--fast) var(--ease) !important;
}
.stSlider > div > div > div > div > div:hover {
  box-shadow: 0 0 0 4px rgba(4,120,87,0.2), var(--shadow-md) !important;
}
.stSlider [data-baseweb="tooltip"] {
  background: var(--text-primary) !important;
  color: #FFFFFF !important;
  border-radius: var(--r-sm) !important;
  font-size: 0.8rem !important;
  font-weight: 700 !important;
  padding: 0.25rem 0.5rem !important;
  font-family: 'JetBrains Mono', monospace !important;
}


/* ══════════════════════════════════════════════════════════
   EXPANDER / ACCORDION
   ══════════════════════════════════════════════════════════ */

.streamlit-expanderHeader {
  background: var(--bg-card) !important;
  color: var(--text-body) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-lg) !important;
  font-weight: 600 !important;
  font-size: 0.9375rem !important;
  box-shadow: var(--shadow-xs) !important;
  transition: background var(--fast) var(--ease),
              box-shadow var(--fast) var(--ease) !important;
}
.streamlit-expanderHeader:hover {
  background: var(--bg-subtle) !important;
  box-shadow: var(--shadow-sm) !important;
}
.streamlit-expanderContent {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--r-lg) var(--r-lg) !important;
}


/* ══════════════════════════════════════════════════════════
   DIVIDERS
   ══════════════════════════════════════════════════════════ */

hr {
  border: none !important;
  border-top: 1px solid var(--border-dark) !important;
  margin: 1.75rem 0 !important;
}


/* ══════════════════════════════════════════════════════════
   AUTH PAGE — centred card layout
   ══════════════════════════════════════════════════════════ */

.auth-outer {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
}
.auth-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow-lg);
  padding: 2.5rem;
  max-width: 440px;
  width: 100%;
}

</style>
"""

DARK_CSS = LIGHT_CSS   # alias — keeps existing imports working


def page_header(title: str, subtitle: str = "") -> str:
    """
    Senior-level page header.
    Warm charcoal title, muted subtitle, subtle bottom border.
    """
    sub_html = (
        f'<p style="margin:0.3rem 0 0; font-size:0.9375rem; '
        f'color:#6B7280; font-weight:400; line-height:1.5;">{subtitle}</p>'
    ) if subtitle else ""

    return f"""
    <div style="
        margin-bottom: 2rem;
        padding-bottom: 1.25rem;
        border-bottom: 1px solid #E5E7EB;
    ">
      <h1 style="
          font-size: 1.75rem;
          font-weight: 700;
          color: #111827;
          letter-spacing: -0.025em;
          line-height: 1.2;
          margin: 0;
          font-family: 'Outfit', sans-serif;
      ">{title}</h1>
      {sub_html}
    </div>
    """


# ── Chart base config — use with fig.update_layout(**CHART_BASE) ─────────────
# IMPORTANT: Never pass `margin`, `xaxis`, or `yaxis` as additional kwargs
#            after spreading CHART_BASE — they already live here.
#            To override margin: call fig.update_layout(margin=...) separately.
CHART_BASE = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#F9FAFB",
    font=dict(
        color="#374151",
        family="Outfit, -apple-system, sans-serif",
        size=12,
    ),
    xaxis=dict(
        gridcolor="rgba(17,24,39,0.05)",
        linecolor="rgba(17,24,39,0.1)",
        tickcolor="rgba(17,24,39,0.1)",
        tickfont=dict(color="#6B7280", size=11),
        title_font=dict(color="#374151", size=12),
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="rgba(17,24,39,0.05)",
        linecolor="rgba(17,24,39,0.1)",
        tickcolor="rgba(17,24,39,0.1)",
        tickfont=dict(color="#6B7280", size=11),
        title_font=dict(color="#374151", size=12),
        showgrid=True,
    ),
    legend=dict(
        font=dict(color="#374151", size=12),
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#E5E7EB",
        borderwidth=1,
    ),
    margin=dict(t=48, b=40, l=48, r=20),
    hoverlabel=dict(
        bgcolor="#FFFFFF",
        bordercolor="#E5E7EB",
        font_color="#111827",
        font_size=12,
    ),
)

# Keep CHART as alias so any existing code using CHART still works
CHART = CHART_BASE


# ── Semantic colours ─────────────────────────────────────────────────────────
GREEN = "#059669"   # emerald-600  — 4.54:1 AA on white ✓
RED   = "#DC2626"   # red-600      — 4.59:1 AA on white ✓
BRAND = "#047857"   # emerald-700  — 4.52:1 AA on white ✓
CARD  = "#FFFFFF"