import streamlit as st
import json
from modules import db, config

st.title("👨‍🏫 Öğretmen Paneli")
user = st.session_state.user_data
if user["role"] not in ["teacher", "admin"]:
    st.error("Bu sayfaya erişim yetkiniz yok.")
    st.stop()

students = db.get_students(user["username"])
if not students:
    st.info("Henüz kayıtlı öğrenci yok.")
    st.stop()

selected_student = st.selectbox("Öğrenci Seç", students)
if selected_student:
    sims = db.get_simulations(selected_student)
    st.subheader(f"{selected_student} - Son Simülasyonlar")
    for sim in sims[:5]:
        data = json.loads(sim["data"])
        with st.expander(f"{config.COUNTRIES[data['country1']]} vs {config.COUNTRIES[data['country2']]} – {data['issue']} ({sim['timestamp'][:10]})"):
            st.json(data)
