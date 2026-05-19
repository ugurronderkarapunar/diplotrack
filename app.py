"""
DiploTrack Pro – AI Destekli Uluslararası İlişkiler Simülasyonu
Tek dosya, SQLite, çok adımlı simülasyon, kredi, öğretmen paneli, AI mentör.
"""
import streamlit as st
import sqlite3
import json
import hashlib
import datetime
import random
import time
import openai
from pathlib import Path

# ---------------------------- SAYFA AYARI ----------------------------
st.set_page_config(page_title="DiploTrack Pro", page_icon="🌐", layout="wide")

# ---------------------------- VERİTABANI ----------------------------
DB_DIR = Path("data")
DB_PATH = DB_DIR / "diplotrack.db"

def get_conn():
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        tier TEXT DEFAULT 'free',
        role TEXT DEFAULT 'student',
        usage_this_month INTEGER DEFAULT 0,
        credits INTEGER DEFAULT 0,
        last_active_month TEXT,
        security_question TEXT,
        security_answer TEXT,
        created_at TEXT,
        badges TEXT DEFAULT '[]'
    );
    CREATE TABLE IF NOT EXISTS simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp TEXT
    );
    CREATE TABLE IF NOT EXISTS credit_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        pack_name TEXT,
        credits_added INTEGER,
        timestamp TEXT
    );
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------------------- YARDIMCI FONKSİYONLAR ----------------------------
def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def get_user(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_user(username, updates):
    conn = get_conn()
    sets = [f"{k}=?" for k in updates]
    vals = list(updates.values()) + [username]
    conn.execute(f"UPDATE users SET {','.join(sets)} WHERE username=?", vals)
    conn.commit()
    conn.close()

def save_user(username, data):
    conn = get_conn()
    keys = list(data.keys())
    vals = [data[k] for k in keys]
    ph = ",".join(["?" for _ in keys])
    cols = ",".join(keys)
    conn.execute(f"INSERT OR REPLACE INTO users ({cols}) VALUES ({ph})", vals)
    conn.commit()
    conn.close()

def add_simulation(username, data_dict, timestamp):
    conn = get_conn()
    conn.execute("INSERT INTO simulations (username,data,timestamp) VALUES (?,?,?)",
                 (username, json.dumps(data_dict), timestamp))
    conn.commit()
    conn.close()

def get_simulations(username):
    conn = get_conn()
    rows = conn.execute("SELECT data, timestamp FROM simulations WHERE username=? ORDER BY timestamp DESC", (username,)).fetchall()
    conn.close()
    return [{"data": json.loads(row["data"]), "timestamp": row["timestamp"]} for row in rows]

def log_action(username, action):
    pass  # isterseniz usage_log tablosu eklenebilir

# ---------------------------- SABİTLER ----------------------------
COUNTRIES = {
    "USA": "🇺🇸", "CHN": "🇨🇳", "RUS": "🇷🇺", "DEU": "🇩🇪",
    "FRA": "🇫🇷", "TUR": "🇹🇷", "IND": "🇮🇳", "BRA": "🇧🇷"
}
COUNTRY_PROFILES = {
    "USA": {"gdp": 25.0, "military": 10, "alliances": ["NATO"]},
    "CHN": {"gdp": 18.0, "military": 9, "alliances": ["ŞİÖ"]},
    "RUS": {"gdp": 2.0, "military": 8, "alliances": ["BDT"]},
    "DEU": {"gdp": 4.5, "military": 5, "alliances": ["NATO", "AB"]},
    "FRA": {"gdp": 3.0, "military": 7, "alliances": ["NATO", "AB"]},
    "TUR": {"gdp": 1.0, "military": 6, "alliances": ["NATO"]},
    "IND": {"gdp": 3.5, "military": 8, "alliances": []},
    "BRA": {"gdp": 2.0, "military": 4, "alliances": ["BRICS"]}
}
ISSUES = ["Ticaret", "Güvenlik", "İklim", "Enerji", "Göç"]
STRATEGIES = ["İşbirlikçi", "Rekabetçi", "Karma"]
THEORY_CARDS = {
    "Realizm": "Güç ve güvenlik odaklı, anarşik sistem.",
    "Liberalizm": "İş birliği ve kurumlar önemlidir.",
    "Konstrüktivizm": "Kimlikler ve normlar belirleyicidir."
}
RESOURCES = [
    "📚 Joseph Nye – ‘Yumuşak Güç’",
    "📚 Hans Morgenthau – ‘Uluslararası Politika’",
    "📚 Robert Keohane – ‘After Hegemony’"
]

# ---------------------------- TEMEL KULLANICI İŞLEMLERİ ----------------------------
def create_default_users():
    if not get_user("demo"):
        save_user("demo", {
            "username": "demo", "password": hash_text("demo123"),
            "tier": "free", "role": "student", "usage_this_month": 0,
            "credits": 0, "last_active_month": datetime.date.today().strftime("%Y-%m"),
            "security_question": "Evcil hayvan?", "security_answer": hash_text("kedi"),
            "created_at": str(datetime.datetime.now()), "badges": "[]"
        })
    if not get_user("ogretmen"):
        save_user("ogretmen", {
            "username": "ogretmen", "password": hash_text("ogretmen123"),
            "tier": "free", "role": "teacher", "usage_this_month": 0,
            "credits": 0, "last_active_month": datetime.date.today().strftime("%Y-%m"),
            "security_question": "En sevdiğiniz ders?", "security_answer": hash_text("tarih"),
            "created_at": str(datetime.datetime.now()), "badges": "[]"
        })

create_default_users()

# ---------------------------- OTURUM YÖNETİMİ ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "sim_session" not in st.session_state:
    st.session_state.sim_session = None

# ---------------------------- CSS TEMA ----------------------------
dark = st.session_state.dark_mode
bg = "#0e1117" if dark else "#ffffff"
text_color = "#fafafa" if dark else "#31333F"
card_bg = "#262730" if dark else "#f0f2f6"
border = "#4b4b4b" if dark else "#d5dae5"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {text_color}; }}
.stApp {{ background-color: {bg}; }}
.stButton>button {{ border-radius: 8px; border: 1px solid {border}; background-color: {card_bg}; color: {text_color}; }}
.stButton>button:hover {{ border-color: #ff4b4b; color: #ff4b4b; }}
.card {{ background: {card_bg}; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid {border}; }}
.badge {{ display: inline-block; background: #ff4b4b; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.8rem; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------- GİRİŞ / KAYIT / ŞİFRE SIFIRLAMA ----------------------------
def login_page():
    st.title("🔐 DiploTrack Giriş")
    st.info("Demo: demo / demo123  |  Öğretmen: ogretmen / ogretmen123")
    page = st.radio("", ["Giriş Yap", "Kayıt Ol", "Şifremi Unuttum"], horizontal=True)

    if page == "Giriş Yap":
        with st.form("login"):
            uname = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                user = get_user(uname)
                if user and user["password"] == hash_text(pw):
                    st.session_state.logged_in = True
                    st.session_state.username = uname
                    st.session_state.user_data = user
                    current_month = datetime.date.today().strftime("%Y-%m")
                    if user["last_active_month"] != current_month:
                        update_user(uname, {"usage_this_month": 0, "last_active_month": current_month})
                        st.session_state.user_data["usage_this_month"] = 0
                    st.rerun()
                else:
                    st.error("Hatalı giriş.")
    elif page == "Kayıt Ol":
        with st.form("register"):
            new_uname = st.text_input("Kullanıcı Adı")
            new_pw = st.text_input("Şifre", type="password")
            sq = st.selectbox("Güvenlik Sorusu", ["Evcil hayvanınızın adı?", "Doğduğunuz şehir?"])
            sa = st.text_input("Cevap")
            role = st.selectbox("Rol", ["student", "teacher"])
            if st.form_submit_button("Kayıt Ol"):
                if get_user(new_uname):
                    st.error("Kullanıcı adı alınmış.")
                else:
                    save_user(new_uname, {
                        "username": new_uname, "password": hash_text(new_pw),
                        "tier": "free", "role": role, "usage_this_month": 0,
                        "credits": 0, "last_active_month": datetime.date.today().strftime("%Y-%m"),
                        "security_question": sq, "security_answer": hash_text(sa.lower()),
                        "created_at": str(datetime.datetime.now()), "badges": "[]"
                    })
                    st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
    else:
        uname = st.text_input("Kullanıcı Adınız")
        user = get_user(uname)
        if user:
            st.write(f"Güvenlik Sorunuz: {user['security_question']}")
            answer = st.text_input("Cevap")
            new_pw = st.text_input("Yeni Şifre", type="password")
            if st.button("Şifreyi Sıfırla"):
                if hash_text(answer.lower()) == user["security_answer"]:
                    update_user(uname, {"password": hash_text(new_pw)})
                    st.success("Şifre sıfırlandı!")
                else:
                    st.error("Cevap yanlış.")
        else:
            st.error("Kullanıcı bulunamadı.")

# ---------------------------- SİMÜLASYON MOTORU ----------------------------
def get_power(country):
    p = COUNTRY_PROFILES.get(country, {"gdp":0.5, "military":0, "alliances":[]})
    return p["gdp"]*0.4 + p["military"]*1.2 + len(p["alliances"])*2

def random_event():
    events = [
        ("Doğal Afet", {"Ekonomi": -15, "Prestij": -5}),
        ("Lider Değişimi", {"Prestij": -10}),
        ("Ekonomik Kriz", {"Ekonomi": -20}),
        ("Teknolojik Atılım", {"Ekonomi": +10, "Prestij": +5})
    ]
    return random.choice(events)

class Simulator:
    def __init__(self, c1, c2, issue, strategy):
        self.c1, self.c2, self.issue, self.strategy = c1, c2, issue, strategy
        self.step = 1
        self.metrics = {"Ekonomi": 0, "Güvenlik": 0, "Prestij": 0}
        self.log = []

    def options(self):
        if self.issue == "Ticaret": return ["Gümrük indirimi", "Yaptırım tehdidi", "Karşılıklı yatırım"]
        if self.issue == "Güvenlik": return ["Askerî iş birliği", "Sınır protokolü", "Silah kontrolü"]
        if self.issue == "İklim": return ["Emisyon hedefi", "Yeşil fon", "Teknoloji transferi"]
        if self.issue == "Enerji": return ["Boru hattı", "Nükleer iş birliği", "Fiyat sabitleme"]
        return ["Kota artırımı", "Geri kabul", "Entegrasyon"]

    def apply(self, decision):
        eff = {m: random.randint(-5, 10) for m in self.metrics}
        if self.strategy == "İşbirlikçi" and "iş birliği" in decision:
            eff["Ekonomi"] += 5; eff["Prestij"] += 3
        elif self.strategy == "Rekabetçi" and ("tehdit" in decision or "yaptırım" in decision):
            eff["Güvenlik"] += 4; eff["Ekonomi"] -= 2
        else:
            eff["Prestij"] += 2
        # Güç dengesi
        if get_power(self.c1) > get_power(self.c2):
            eff["Prestij"] += 2
        # Rastgele olay
        event = None
        if random.random() < 0.4:
            event = random_event()
            for k, v in event[1].items():
                eff[k] = eff.get(k, 0) + v
        for k in eff:
            self.metrics[k] += eff[k]
        self.log.append({"step": self.step, "decision": decision, "effects": eff, "event": event})
        self.step += 1
        return self.step > 3  # 3 adımda biter

    def finalize(self):
        total = sum(self.metrics.values())
        result = "Başarılı" if total > 15 else ("Kısmi" if total > 0 else "Başarısız")
        analysis = {
            "İşbirlikçi": "Uzun vadeli kazanç.",
            "Rekabetçi": "Kısa vadeli kazanç, güven sarsıldı.",
            "Karma": "Dengeli sonuç."
        }[self.strategy]
        theory = "Realizm" if self.issue in ["Güvenlik","Enerji"] else ("Liberalizm" if self.issue in ["Ticaret","Göç"] else "Konstrüktivizm")
        return {
            "country1": self.c1, "country2": self.c2, "issue": self.issue,
            "strategy": self.strategy, "metrics": self.metrics, "total_score": total,
            "result": result, "analysis": analysis, "theory": theory,
            "theory_desc": THEORY_CARDS[theory],
            "resource": random.choice(RESOURCES),
            "log": self.log, "timestamp": datetime.datetime.now().isoformat()
        }

# ---------------------------- AI MENTÖR (OpenAI) ----------------------------
def ai_coach_available():
    return "OPENAI_API_KEY" in st.secrets

def ask_ai_coach(situation, theory="Realizm"):
    if not ai_coach_available():
        return "AI mentör için OpenAI API anahtarı gerekli. (Şu an çevrimdışı)"
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    prompt = f"Sen bir IR profesörüsün. Şu müzakere durumu için {theory} perspektifinden kısa bir strateji tavsiyesi ver (Türkçe, 3 cümle):\n{situation}"
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=150
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"AI hatası: {e}"

# ---------------------------- SAYFALAR ----------------------------
def dashboard():
    st.title("📊 Panel")
    user = st.session_state.user_data
    sims = get_simulations(user["username"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Abonelik", user["tier"].upper())
    limit = "∞" if user["tier"]=="pro" else f"3 + {user['credits']} kredi"
    col2.metric("Bu Ay Kullanım", f"{user['usage_this_month']} / {limit}")
    col3.metric("Toplam Simülasyon", len(sims))
    if user["tier"]=="free" and user["usage_this_month"] >= 3 and user["credits"]==0:
        st.warning("Limite ulaştınız. Kredi alın veya Pro'ya geçin.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🛒 Kredi Al"): st.session_state.page = "credits"; st.rerun()
        with c2:
            if st.button("💎 Pro Yükselt"): st.session_state.page = "upgrade"; st.rerun()

def simulator():
    st.title("🌐 Simülatör")
    user = st.session_state.user_data
    allowed = 3 + user["credits"] if user["tier"]=="free" else 999
    if user["usage_this_month"] >= allowed:
        st.error("Limit doldu.")
        if st.button("Kredi Al"): st.session_state.page = "credits"; st.rerun()
        return
    if st.session_state.sim_session is None:
        with st.form("new_sim"):
            c1 = st.selectbox("Ülke 1", list(COUNTRIES.keys()))
            c2 = st.selectbox("Ülke 2", list(COUNTRIES.keys()), index=1)
            issue = st.selectbox("Konu", ISSUES)
            strategy = st.selectbox("Strateji", STRATEGIES)
            if st.form_submit_button("Başlat"):
                st.session_state.sim_session = Simulator(c1, c2, issue, strategy)
                st.rerun()
    else:
        ses = st.session_state.sim_session
        st.markdown(f"**{COUNTRIES[ses.c1]} {ses.c1} vs {COUNTRIES[ses.c2]} {ses.c2}**")
        st.progress((ses.step-1)/3)
        if ses.step <= 3:
            st.subheader(f"Adım {ses.step}/3")
            dec = st.radio("Kararınız:", ses.options())
            # AI Tavsiye butonu
            if st.button("🤖 AI Mentörden Tavsiye Al"):
                situation = f"{ses.c1} ile {ses.c2} arasında {ses.issue} müzakere ediliyor, strateji {ses.strategy}. Mevcut metrikler: {ses.metrics}"
                advice = ask_ai_coach(situation, ses.theory if hasattr(ses,'theory') else "Realizm")
                st.info(f"**AI Mentör:** {advice}")
            if st.button("Kararı Uygula"):
                done = ses.apply(dec)
                if done:
                    final = ses.finalize()
                    # Kullanım sayacı
                    update_user(st.session_state.username, {"usage_this_month": user["usage_this_month"]+1})
                    st.session_state.user_data["usage_this_month"] += 1
                    add_simulation(st.session_state.username, final, final["timestamp"])
                    st.session_state.sim_session = None
                    st.success("Simülasyon tamamlandı!")
                    st.rerun()
                else:
                    st.rerun()

def history():
    st.title("📁 Geçmiş")
    sims = get_simulations(st.session_state.username)
    if not sims: st.info("Henüz simülasyon yok."); return
    for s in sims:
        d = s["data"]
        with st.expander(f"{COUNTRIES[d['country1']]} vs {COUNTRIES[d['country2']]} – {d['issue']} ({s['timestamp'][:10]})"):
            st.write(f"Strateji: {d['strategy']}, Skor: {d['total_score']}")
            st.write(f"Metrikler: {d['metrics']}")
            st.write(f"Sonuç: {d['result']} - {d['analysis']}")
            st.write(f"Teori: {d['theory']} – {d['theory_desc']}")

def upgrade():
    st.title("💎 Pro Üyelik")
    if st.session_state.user_data["tier"]=="pro":
        st.success("Zaten Pro'sunuz."); return
    if st.button("💳 Ödeme Yap (Simülasyon)"):
        update_user(st.session_state.username, {"tier": "pro"})
        st.session_state.user_data = get_user(st.session_state.username)
        st.success("Pro oldunuz!"); st.balloons()
        st.session_state.page = "dashboard"; st.rerun()

def credits():
    st.title("🛒 Kredi Satın Al")
    packs = {"10 Kredi (10 simülasyon)": 10, "30 Kredi": 30}
    choice = st.selectbox("Paket", list(packs.keys()))
    if st.button("Satın Al (Mock)"):
        cred = packs[choice]
        update_user(st.session_state.username, {"credits": st.session_state.user_data["credits"] + cred})
        st.session_state.user_data = get_user(st.session_state.username)
        st.success(f"{cred} kredi eklendi!"); st.balloons()
        st.session_state.page = "dashboard"; st.rerun()

def teacher_panel():
    st.title("👨‍🏫 Öğretmen Paneli")
    if st.session_state.user_data["role"] not in ["teacher","admin"]:
        st.error("Yetkisiz erişim."); return
    conn = get_conn()
    students = [row["username"] for row in conn.execute("SELECT username FROM users WHERE role='student'").fetchall()]
    conn.close()
    if not students: st.info("Öğrenci yok."); return
    sel = st.selectbox("Öğrenci Seç", students)
    if sel:
        sims = get_simulations(sel)
        for s in sims[:5]:
            with st.expander(f"{s['data']['country1']} vs {s['data']['country2']} – {s['timestamp'][:10]}"):
                st.json(s["data"])

# ---------------------------- ANA UYGULAMA ----------------------------
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    # Sidebar
    with st.sidebar:
        st.write(f"👤 {st.session_state.username} ({st.session_state.user_data['role']})")
        if st.button("🌓 Tema"): st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()
        st.write("---")
        menu = ["📊 Panel", "🌐 Simülatör", "📁 Geçmiş", "💎 Pro Yükselt", "🛒 Kredi Al"]
        if st.session_state.user_data["role"] in ["teacher","admin"]:
            menu.append("👨‍🏫 Öğretmen")
        choice = st.radio("Menü", menu)

        if st.button("Çıkış Yap"):
            for k in ["logged_in","username","user_data","sim_session"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    # Sayfa yönlendirme
    page = choice.split(" ")[1] if " " in choice else choice
    mapping = {
        "Panel": dashboard, "Simülatör": simulator, "Geçmiş": history,
        "Pro Yükselt": upgrade, "Kredi Al": credits, "Öğretmen": teacher_panel
    }
    mapping.get(page, dashboard)()

if __name__ == "__main__":
    main()
