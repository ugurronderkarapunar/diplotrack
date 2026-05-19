import streamlit as st
from modules import db, utils

st.title("💎 Pro Üyelik")
st.markdown("### Aylık ₺199 (mock)")
st.write("- Sınırsız simülasyon")
st.write("- Tüm rozetler ve detaylı analiz")
st.write("- Öncelikli destek")

if st.session_state.user_data["tier"] == "pro":
    st.success("Zaten Pro üyesisiniz.")
    st.stop()

if st.button("💳 Ödeme Yap ve Pro’ya Geç"):
    db.update_user(st.session_state.username, {"tier": "pro"})
    st.session_state.user_data = db.get_user(st.session_state.username)
    utils.check_and_award_badges(st.session_state.username)
    st.success("Pro oldunuz! Yönlendiriliyorsunuz...")
    st.balloons()
    st.switch_page("pages/1_📊_Dashboard.py")
