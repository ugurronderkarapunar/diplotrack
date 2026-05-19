import streamlit as st
from modules import db, config

st.title("📁 Kayıtlı Simülasyonlar")
sims = db.load_user_simulations(st.session_state.username)
if not sims:
    st.info("Henüz simülasyon yok.")
    st.stop()

filtre_issue = st.selectbox("Konu Filtrele", ["Hepsi"] + config.ISSUES)
for sim in sims:
    if filtre_issue != "Hepsi" and sim["issue"] != filtre_issue:
        continue
    with st.expander(f"{config.COUNTRIES[sim['country1']]} {sim['country1']} vs {config.COUNTRIES[sim['country2']]} {sim['country2']} – {sim['issue']} ({sim['timestamp'][:10]})"):
        st.markdown(f"**Strateji:** {sim['strategy']} | **Sonuç:** {sim['result']}")
        st.markdown(f"**Analiz:** {sim['analysis']}")
        st.markdown(f"**Teori:** {sim['theory']} – {sim['theory_desc']}")
