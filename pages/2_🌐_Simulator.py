import streamlit as st
import json
from modules import config, engine, db, utils

st.title("🌐 Diplomasi Simülatörü")
user = st.session_state.user_data

# Kullanım hakkı kontrolü
if user["tier"] == "free":
    allowed = 3 + user["credits"]
    if user["usage_this_month"] >= allowed:
        st.error("Tüm kullanım hakkınız doldu. Kredi alın veya Pro’ya geçin.")
        if st.button("Kredi Al"):
            st.switch_page("pages/5_🛒_Credits.py")
        st.stop()

# Session state'te aktif simülasyonu tut
if "sim_session" not in st.session_state:
    st.session_state.sim_session = None

if st.session_state.sim_session is None:
    # Başlangıç formu
    with st.form("new_sim"):
        c1 = st.selectbox("Ülke 1", list(config.COUNTRIES.keys()))
        c2 = st.selectbox("Ülke 2", list(config.COUNTRIES.keys()), index=1)
        issue = st.selectbox("Konu", config.ISSUES)
        strategy = st.selectbox("Strateji", config.STRATEGIES)
        if st.form_submit_button("Müzakereyi Başlat"):
            ses = engine.SimulatorSession(c1, c2, issue, strategy)
            st.session_state.sim_session = ses
            st.rerun()
else:
    ses = st.session_state.sim_session
    st.markdown(f"**{config.COUNTRIES[ses.country1]} {ses.country1}** vs **{config.COUNTRIES[ses.country2]} {ses.country2}**")
    st.progress((ses.step-1)/ses.total_steps)

    if not ses.finished:
        st.subheader(f"Adım {ses.step}/{ses.total_steps}")
        options = ses.get_options()
        decision = st.radio("Kararınız:", options)
        if st.button("Kararı Uygula"):
            ses.apply_decision(decision)
            if ses.finished:
                # Simülasyonu bitir, kaydet
                final = ses.get_final_result()
                # Kullanım sayacı
                user["usage_this_month"] += 1
                db.update_user(st.session_state.username, {"usage_this_month": user["usage_this_month"]})
                st.session_state.user_data = db.get_user(st.session_state.username)
                # Kaydet
                db.add_simulation(st.session_state.username, json.dumps(final), final["timestamp"])
                db.log_action(st.session_state.username, "simulation_complete")
                utils.check_and_award_badges(st.session_state.username)
                st.session_state.sim_session = None
                st.rerun()
            else:
                st.rerun()
    else:
        # Bu durum olmamalı, finished olduğunda otomatik resetlenir
        st.session_state.sim_session = None
        st.rerun()
