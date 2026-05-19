import streamlit as st
from modules import db, utils

st.title("📊 Panel")
user = st.session_state.user_data

col1, col2, col3 = st.columns(3)
col1.metric("Abonelik", user["tier"].upper())
limit = "∞" if user["tier"] == "pro" else "3"
col2.metric("Bu Ay Kullanım", f"{user['usage_this_month']} / {limit}")
col3.metric("Toplam Simülasyon", len(db.load_user_simulations(st.session_state.username)))

# Rozetler
if user.get("badges"):
    st.markdown("### 🏆 Rozetleriniz")
    badge_str = " ".join([f"<span class='badge'>{utils.config.BADGES[b]['name']}</span>" for b in user["badges"]])
    st.markdown(badge_str, unsafe_allow_html=True)

# Grafikler
charts = utils.prepare_dashboard_charts(st.session_state.username)
if charts["months"]:
    st.line_chart({"Kullanım": charts["month_counts"]})
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(charts["country_freq"])
    with col2:
        st.bar_chart(charts["strategy_freq"])

if user["tier"] == "free":
    st.warning("Ayda 3 simülasyon hakkınız var. Sınırsız için Pro’ya geçin.")
    if st.button("🚀 Pro’ya Yükselt"):
        st.switch_page("pages/4_💎_Upgrade.py")
