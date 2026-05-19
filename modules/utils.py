import streamlit as st
import time
from . import config, db

# --- Tema ---
def apply_theme():
    dark = st.session_state.get("dark_mode", False)
    bg = "#0e1117" if dark else "#ffffff"
    text = "#fafafa" if dark else "#31333F"
    card_bg = "#262730" if dark else "#f0f2f6"
    border = "#4b4b4b" if dark else "#d5dae5"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif;
        color: {text};
    }}
    .stApp {{
        background-color: {bg};
    }}
    .stButton>button {{
        border-radius: 8px;
        border: 1px solid {border};
        background-color: {card_bg};
        color: {text};
        transition: 0.2s;
    }}
    .stButton>button:hover {{
        border-color: #ff4b4b;
        color: #ff4b4b;
    }}
    .card {{
        background: {card_bg};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid {border};
    }}
    .badge {{
        display: inline-block;
        background: #ff4b4b;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }}
    .flag {{
        font-size: 2rem;
    }}
    .invoice-box {{
        background: {card_bg};
        padding: 20px;
        border: 1px solid {border};
        font-family: monospace;
        white-space: pre-wrap;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Oturum süresi kontrolü ---
def check_session_timeout():
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
    else:
        idle_time = time.time() - st.session_state.last_activity
        if idle_time > 300:  # 5 dakika
            st.warning("Oturum süresi doldu. Lütfen tekrar giriş yapın.")
            for key in ["logged_in", "username", "user_data", "last_activity"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    st.session_state.last_activity = time.time()

# --- Rozet kontrolü ---
def check_and_award_badges(username):
    user = db.get_user(username)
    badges = eval(user["badges"]) if user["badges"] else []
    sims = [eval(s["data"]) for s in db.get_simulations(username)]
    new_badges = []

    if len(sims) >= 1 and "first_sim" not in badges:
        new_badges.append("first_sim")
    issues_used = {s["issue"] for s in sims}
    if len(issues_used) == len(config.ISSUES) and "explorer" not in badges:
        new_badges.append("explorer")
    strategies_used = {s["strategy"] for s in sims}
    if len(strategies_used) == len(config.STRATEGIES) and "strategist" not in badges:
        new_badges.append("strategist")
    if user["tier"] == "pro" and "pro_member" not in badges:
        new_badges.append("pro_member")
    if user["credits"] > 0 and "credit_buyer" not in badges:
        new_badges.append("credit_buyer")

    for b in new_badges:
        badges.append(b)
        st.toast(f"🏆 Rozet kazandınız: {config.BADGES[b]['name']}!", icon="🎉")
        st.balloons()
    if new_badges:
        db.update_user(username, {"badges": str(badges)})

# --- Grafik verisi (SQLite'dan) ---
def prepare_dashboard_charts(username):
    sims = [eval(s["data"]) for s in db.get_simulations(username)]
    months = {}
    country_freq = {}
    issue_freq = {}
    strategy_freq = {}
    for s in sims:
        m = s["timestamp"][:7]
        months[m] = months.get(m, 0) + 1
        c = s["country1"]
        country_freq[c] = country_freq.get(c, 0) + 1
        i = s["issue"]
        issue_freq[i] = issue_freq.get(i, 0) + 1
        strat = s["strategy"]
        strategy_freq[strat] = strategy_freq.get(strat, 0) + 1
    month_list = sorted(months.keys())[-6:]
    counts = [months[m] for m in month_list]
    return {
        "months": month_list,
        "month_counts": counts,
        "country_freq": country_freq,
        "issue_freq": issue_freq,
        "strategy_freq": strategy_freq
    }

# --- Fatura metni ---
def generate_invoice(username, item, amount):
    return f"""
FATURA
----------
Tarih: {time.strftime('%Y-%m-%d %H:%M')}
Müşteri: {username}
Ürün: {item}
Tutar: {amount} TL (mock)
Bu bir simülasyon faturasıdır, gerçek değildir.
"""
