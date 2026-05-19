import streamlit as st
import time
from modules import config, engine, db, utils

st.title("🌐 Diplomasi Simülatörü")
user = st.session_state.user_data

if not (user["tier"] == "pro" or user["usage_this_month"] < 3):
    st.error("Bu ayki limitiniz doldu. Pro ile sınırsız simülasyon yapın.")
    if st.button("Pro’ya Yükselt"):
        st.switch_page("pages/4_💎_Upgrade.py")
    st.stop()

with st.form("sim_form"):
    col1, col2 = st.columns(2)
    with col1:
        c1 = st.selectbox("Ülke 1", list(config.COUNTRIES.keys()))
        c2 = st.selectbox("Ülke 2", list(config.COUNTRIES.keys()), index=1)
    with col2:
        issue = st.selectbox("Konu", config.ISSUES)
        strategy = st.selectbox("Strateji", config.STRATEGIES)
    run = st.form_submit_button("Simülasyonu Başlat")

if run:
    # Çok adımlı ilerleme
    progress = st.progress(0)
    status = st.empty()
    for i in range(3):
        status.text(f"Adım {i+1}/3: {['Ön görüşme', 'Pozisyon belirleme', 'Anlaşma taslağı'][i]}")
        time.sleep(0.5)
        progress.progress((i+1)/3)
    status.empty()
    progress.empty()

    # Simülasyonu çalıştır
    sim = engine.run_multi_step_simulation(c1, c2, issue, strategy)
    # Kullanımı artır ve kaydet
    user["usage_this_month"] += 1
    db.update_user(st.session_state.username, {"usage_this_month": user["usage_this_month"]})
    st.session_state.user_data = db.get_user(st.session_state.username)
    db.save_simulation(st.session_state.username, sim)
    utils.check_and_award_badges(st.session_state.username)

    # Kart tasarımı ile sonuç
    st.markdown(f"""
    <div class="card">
        <h2>{config.COUNTRIES[sim['country1']]} {sim['country1']} vs {config.COUNTRIES[sim['country2']]} {sim['country2']}</h2>
        <p><b>Konu:</b> {sim['issue']} | <b>Strateji:</b> <span style="color:#ff4b4b;">{sim['strategy']}</span></p>
        <p><b>Sonuç:</b> {sim['result']}</p>
        <hr>
        <p><b>Analiz:</b> {sim['analysis']}</p>
        <p><b>Toplam Skor:</b> {sim['total_score']}</p>
        <p>📊 {', '.join(f'{k}: {v:+d}' for k,v in sim['metrics'].items())}</p>
        <hr>
        <h4>📖 Teori Kartı: {sim['theory']}</h4>
        <p>{sim['theory_desc']}</p>
        <p>📚 Önerilen Kaynak: {sim['resource']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Karşılaştırma butonu
    if st.button("🔄 Aynı senaryoyu farklı stratejiyle karşılaştır"):
        other_strategy = [s for s in config.STRATEGIES if s != strategy][0]
        sim2 = engine.run_multi_step_simulation(c1, c2, issue, other_strategy)
        db.save_simulation(st.session_state.username, sim2)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Strateji: {sim['strategy']}** – Skor: {sim['total_score']}")
        with col2:
            st.markdown(f"**Strateji: {sim2['strategy']}** – Skor: {sim2['total_score']}")
