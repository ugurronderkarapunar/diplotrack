"""
DiploTrack - Uluslararası İlişkiler Diplomasi Simülasyon SaaS (Streamlit MVP)
Monetization: Freemium (aylık limit) → Pro abonelik (mock)
Tek repo, harici servis yok, local JSON storage, session bazlı auth.
Otomatik demo kullanıcı oluşturma eklendi.
"""

import streamlit as st
import json
import hashlib
import datetime
import random
import os
from pathlib import Path

# ---------------------------- VERİ KATMANI ----------------------------
DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
SIMULATIONS_DIR = DATA_DIR / "simulations"

st.set_page_config(page_title="DiploTrack", layout="wide")

def init_data():
    """Klasörleri, kullanıcı dosyasını ve varsayılan demo kullanıcıyı oluştur."""
    DATA_DIR.mkdir(exist_ok=True)
    SIMULATIONS_DIR.mkdir(exist_ok=True)
    if not USERS_FILE.exists():
        # İlk kez çalıştırılıyor, boş bir users.json oluştur
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def create_default_user():
    """Eğer hiç kullanıcı yoksa demo kullanıcısı ekle."""
    users = load_users()
    if not users:
        users["demo"] = {
            "password": hash_password("demo123"),
            "tier": "free",
            "usage_this_month": 0,
            "last_active_month": datetime.date.today().strftime("%Y-%m"),
            "created_at": str(datetime.datetime.now())
        }
        save_users(users)

def get_user_sim_dir(username: str) -> Path:
    d = SIMULATIONS_DIR / username
    d.mkdir(exist_ok=True)
    return d

# ---------------------------- OTOURİZASYON YARDIMCILARI ----------------------------
def login_user(username: str, password: str) -> bool:
    users = load_users()
    user = users.get(username)
    if user and user["password"] == hash_password(password):
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_data"] = user
        # Yeni ay kontrolü
        current_month = datetime.date.today().strftime("%Y-%m")
        if user.get("last_active_month") != current_month:
            user["usage_this_month"] = 0
            user["last_active_month"] = current_month
            save_users(users)
            st.session_state["user_data"] = user
        return True
    return False

def register_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "tier": "free",
        "usage_this_month": 0,
        "last_active_month": datetime.date.today().strftime("%Y-%m"),
        "created_at": str(datetime.datetime.now())
    }
    save_users(users)
    return True

def update_user_tier(username: str, tier: str):
    users = load_users()
    if username in users:
        users[username]["tier"] = tier
        save_users(users)
        st.session_state["user_data"]["tier"] = tier

def increment_usage():
    users = load_users()
    uname = st.session_state["username"]
    users[uname]["usage_this_month"] += 1
    save_users(users)
    st.session_state["user_data"]["usage_this_month"] = users[uname]["usage_this_month"]

def can_run_simulation() -> bool:
    user = st.session_state["user_data"]
    if user["tier"] == "pro":
        return True
    return user["usage_this_month"] < 3

# ---------------------------- SİMÜLASYON MOTORU ----------------------------
COUNTRIES = ["ABD", "Çin", "Rusya", "Almanya", "Fransa", "Türkiye", "Hindistan", "Brezilya"]
ISSUES = ["Ticaret", "Güvenlik", "İklim", "Enerji", "Göç"]
STRATEGIES = ["İşbirlikçi", "Rekabetçi", "Karma"]

def generate_simulation(country1, country2, issue, strategy):
    outcomes = {
        "Ticaret": [
            "Gümrük tarifelerinde %10 indirim sağlandı.",
            "Serbest ticaret anlaşması imzalandı.",
            "Müzakereler çıkmaza girdi, yaptırımlar devam ediyor."
        ],
        "Güvenlik": [
            "Askerî iş birliği protokolü imzalandı.",
            "Sınır güvenliği konusunda ortak devriye kararı alındı.",
            "Silah satışı konusunda anlaşmaya varılamadı."
        ],
        "İklim": [
            "Karbon emisyonu hedefleri ortak açıklandı.",
            "Yeşil enerji fonu oluşturuldu.",
            "Anlaşma sağlanamadı, müzakereler ertelendi."
        ],
        "Enerji": [
            "Doğal gaz boru hattı projesinde mutabakata varıldı.",
            "Nükleer enerji iş birliği başlatıldı.",
            "Enerji fiyatları konusunda uzlaşma sağlanamadı."
        ],
        "Göç": [
            "Mülteci kotaları konusunda anlaşma sağlandı.",
            "Geri kabul anlaşması imzalandı.",
            "Görüşmeler sonuçsuz kaldı."
        ]
    }
    advices = {
        "İşbirlikçi": "Karşılıklı kazanç odaklı strateji olumlu sonuç verdi.",
        "Rekabetçi": "Sert pazarlık taktiği kısa vadede avantaj sağlasa da uzun vadeli iş birliğini zora soktu.",
        "Karma": "Dengeli strateji ile her iki taraf da kısmen tatmin oldu."
    }
    result_text = random.choice(outcomes.get(issue, ["Müzakereler sonuçsuz kaldı."]))
    advice = advices.get(strategy, "")
    return {
        "country1": country1,
        "country2": country2,
        "issue": issue,
        "strategy": strategy,
        "result": result_text,
        "analysis": advice,
        "timestamp": datetime.datetime.now().isoformat()
    }

def save_simulation(username, sim_data):
    user_dir = get_user_sim_dir(username)
    sim_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filepath = user_dir / f"{sim_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sim_data, f, indent=2, ensure_ascii=False)
    return filepath

def load_user_simulations(username):
    user_dir = get_user_sim_dir(username)
    sims = []
    for f in sorted(user_dir.glob("*.json"), reverse=True):
        with open(f, "r", encoding="utf-8") as fp:
            sims.append(json.load(fp))
    return sims

# ---------------------------- SAYFALAR ----------------------------
def login_page():
    st.title("🔐 DiploTrack Giriş")
    st.info("💡 İlk kez mi geliyorsunuz? Demo hesap ile hemen başlayın: **demo / demo123**")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab1:
        with st.form("login_form"):
            uname = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            submitted = st.form_submit_button("Giriş")
            if submitted:
                if login_user(uname, pw):
                    st.success("Başarıyla giriş yapıldı.")
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre.")
    with tab2:
        with st.form("register_form"):
            new_uname = st.text_input("Yeni Kullanıcı Adı")
            new_pw = st.text_input("Yeni Şifre", type="password")
            reg_submitted = st.form_submit_button("Kayıt Ol")
            if reg_submitted:
                if register_user(new_uname, new_pw):
                    st.success("Kayıt başarılı! Lütfen giriş yapın.")
                else:
                    st.error("Bu kullanıcı adı zaten alınmış.")

def logout():
    for key in ["logged_in", "username", "user_data"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def dashboard_page():
    st.title("📊 Panel")
    user = st.session_state["user_data"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Abonelik", user["tier"].upper())
    with col2:
        limit = "∞" if user["tier"] == "pro" else "3"
        st.metric("Bu Ay Kullanım", f"{user['usage_this_month']} / {limit}")
    with col3:
        st.metric("Kayıtlı Simülasyon", len(load_user_simulations(st.session_state["username"])))
    st.markdown("---")
    if user["tier"] == "free":
        st.warning("Ücretsiz planda ayda 3 simülasyon hakkınız var. Sınırsız erişim için Pro’ya yükseltin.")
        if st.button("🚀 Pro’ya Yükselt"):
            st.session_state["page"] = "upgrade"
            st.rerun()

def simulator_page():
    st.title("🌐 Diplomasi Simülatörü")
    if not can_run_simulation():
        st.error("Bu ayki simülasyon limitinize ulaştınız (3/3). Daha fazlası için Pro üyeliğe geçin.")
        if st.button("Pro’ya Yükselt"):
            st.session_state["page"] = "upgrade"
            st.rerun()
        return

    with st.form("sim_form"):
        col1, col2 = st.columns(2)
        with col1:
            country1 = st.selectbox("Ülke 1", COUNTRIES)
            country2 = st.selectbox("Ülke 2", COUNTRIES, index=1)
        with col2:
            issue = st.selectbox("Konu", ISSUES)
            strategy = st.selectbox("Strateji", STRATEGIES)
        run_sim = st.form_submit_button("Simülasyonu Başlat")
    if run_sim:
        sim = generate_simulation(country1, country2, issue, strategy)
        st.success("Simülasyon tamamlandı!")
        st.json(sim)
        increment_usage()
        save_simulation(st.session_state["username"], sim)
        st.info("Sonuç kaydedildi.")

def saved_page():
    st.title("📁 Kayıtlı Simülasyonlar")
    sims = load_user_simulations(st.session_state["username"])
    if not sims:
        st.info("Henüz kayıtlı simülasyon yok.")
        return
    for i, sim in enumerate(sims):
        with st.expander(f"{sim['country1']} - {sim['country2']} | {sim['issue']} ({sim['timestamp'][:10]})"):
            st.write(f"**Strateji:** {sim['strategy']}")
            st.write(f"**Sonuç:** {sim['result']}")
            st.write(f"**Analiz:** {sim['analysis']}")

def upgrade_page():
    st.title("💎 Pro Üyelik")
    st.markdown("### Aylık ₺199 (mock)")
    st.write("- Sınırsız simülasyon")
    st.write("- Tüm geçmişe erişim")
    st.write("- Gelişmiş analiz ve rapor çıktısı (yakında)")
    if st.session_state["user_data"]["tier"] == "pro":
        st.success("Zaten Pro üyesisiniz. Teşekkürler!")
        return
    st.markdown("---")
    st.write("**Ödeme simülasyonu** – gerçek bir ödeme altyapısı yoktur.")
    if st.button("💳 Ödeme Yap ve Pro’ya Geç"):
        update_user_tier(st.session_state["username"], "pro")
        st.success("Pro üyeliğiniz aktif! Yönlendiriliyorsunuz...")
        st.balloons()
        st.session_state["page"] = "dashboard"
        st.rerun()

# ---------------------------- ANA UYGULAMA ----------------------------
def main():
    init_data()
    create_default_user()  # Eğer hiç kullanıcı yoksa demo eklenir

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"

    if not st.session_state["logged_in"]:
        login_page()
        return

    # Sidebar navigasyon
    page_map = {
        "dashboard": "📊 Panel",
        "simulator": "🌐 Simülatör",
        "saved": "📁 Kayıtlar",
        "upgrade": "💎 Pro Yükselt"
    }
    current_page_id = st.session_state.get("page", "dashboard")
    page_names = list(page_map.values())
    page_ids = list(page_map.keys())
    default_index = page_ids.index(current_page_id) if current_page_id in page_ids else 0

    st.sidebar.title(f"👤 {st.session_state['username']}")
    selected_page_name = st.sidebar.radio(
        "Menü",
        page_names,
        index=default_index,
        key="nav_radio"
    )
    selected_index = page_names.index(selected_page_name)
    selected_page_id = page_ids[selected_index]
    st.session_state["page"] = selected_page_id

    if selected_page_id == "dashboard":
        dashboard_page()
    elif selected_page_id == "simulator":
        simulator_page()
    elif selected_page_id == "saved":
        saved_page()
    elif selected_page_id == "upgrade":
        upgrade_page()

    st.sidebar.markdown("---")
    if st.sidebar.button("Çıkış Yap"):
        logout()

if __name__ == "__main__":
    main()
