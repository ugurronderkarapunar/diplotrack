import streamlit as st
from modules import db, utils

st.title("🛒 Kredi Satın Al")
st.write("Her paket 10 simülasyon hakkı ekler.")

packs = {
    "Küçük Paket (10 kredi)": 10,
    "Büyük Paket (30 kredi)": 30
}

choice = st.selectbox("Paket Seçin", list(packs.keys()))
if st.button("Satın Al (Mock Ödeme)"):
    credits = packs[choice]
    current = st.session_state.user_data["credits"]
    db.update_user(st.session_state.username, {"credits": current + credits})
    db.add_credit_purchase(st.session_state.username, choice, credits)
    db.log_action(st.session_state.username, f"buy_credits_{credits}")
    st.session_state.user_data = db.get_user(st.session_state.username)
    utils.check_and_award_badges(st.session_state.username)
    invoice = utils.generate_invoice(st.session_state.username, choice, f"{credits*5} TL")
    st.text_area("Fatura", invoice, height=150)
    st.success(f"{credits} kredi hesabınıza eklendi!")
    st.balloons()
