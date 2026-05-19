import streamlit as st
from modules import db, utils

st.title("💎 Pro Üyelik")
st.markdown("### Aylık ₺199 (mock)")
st.write("- Sınırsız simülasyon")
st.write("- Öğretmen paneli (rolünüz öğretmen ise)")
st.write("- Tüm istatistikler ve öncelikli destek")

if st.session_state.user_data["tier"] == "pro":
    st.success("Zaten Pro'sunuz.")
    st.stop()

if st.button("💳 Ödeme Yap (Simülasyon)"):
    db.update_user(st.session_state.username, {"tier": "pro"})
    st.session_state.user_data = db.get_user(st.session_state.username)
    utils.check_and_award_badges(st.session_state.username)
    invoice = utils.generate_invoice(st.session_state.username, "Pro Abonelik", "199 TL")
    st.text_area("Fatura", invoice, height=150)
    st.success("Pro oldunuz!")
    st.balloons()
    st.switch_page("pages/1_📊_Dashboard.py")
