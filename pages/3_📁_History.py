import streamlit as st
import json
from modules import db, config

st.title("📁 Geçmiş Simülasyonlar")
sims = db.get_simulations(st.session_state.username)
if not sims:
    st.info("Henüz simülasyon yok.")
    st.stop()

filtre = st.selectbox("Konu Filtrele", ["Hepsi"] + config.ISSUES)
for sim in sims:
    data = json.loads(sim["data"])
    if filtre != "Hepsi" and data["issue"] != filtre:
        continue
    with st.expander(f"{config.COUNTRIES[data['country1']]} vs {config.COUNTRIES[data['country2']]} – {data['issue']} ({sim['timestamp'][:10]})"):
        st.write(f"**Strateji:** {data['strategy']}")
        st.write(f"**Sonuç:** {data['result']}")
        st.write(f"**Skor:** {data['total_score']}")
        st.write(f"**Metrikler:** {data['metrics']}")
        st.write(f"**Analiz:** {data['analysis']}")
        st.write(f"**Teori:** {data['theory']} – {data['theory_desc']}")
