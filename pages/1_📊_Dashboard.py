import streamlit as st
from modules import db, utils

st.title("📊 Panel")
user = st.session_state.user_data

col1, col2, col3 = st.columns(3)
col1.metric("Abonelik", user["tier"].upper())
limit = "∞" if user["tier"] == "pro" else f"3 + {user['credits']} kredi"
col2.metric("Bu Ay Kullanım", f"{user['usage_this_month']} / {limit}")
col3.metric("Toplam Simülasyon", len(db.get_simulations(st.session_state.username)))

badges = eval(user.get("badges", "[]"))
if badges:
    badge_html = " ".join([f"<span class='badge'>{utils.config.BADGES[b]['name']}</span>" for b in badges])
    st.markdown(badge_html, unsafe_allow_html=True)

charts = utils.prepare_dashboard_charts(st.session_state.username)
if charts["months"]:
    st.line_chart({"Kullanım": charts["month_counts"]})
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(charts["country_freq"])
    with col2:
        st.bar_chart(charts["strategy_freq"])

if user["tier"] == "free" and user["usage_this_month"] >= 3 and user["credits"] == 0:
    st.warning("Aylık limitiniz doldu. Kredi satın alabilir veya Pro’ya geçebilirsiniz.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Kredi Al"):
            st.switch_page("pages/5_🛒_Credits.py")
    with c2:
        if st.button("Pro Yükselt"):
            st.switch_page("pages/4_💎_Upgrade.py")
