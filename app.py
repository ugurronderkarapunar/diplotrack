import streamlit as st
from pathlib import Path
from modules import auth, db, utils

# --- SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="DiploTrack", page_icon="🌐", layout="wide")

# --- VERİ BAŞLATMA ---
db.init_data()
auth.create_default_user()

# --- TEMAYI UYGULA ---
utils.apply_theme()

# --- SIDEBAR İŞLEMLERİ ---
if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False

if st.session_state.sidebar_collapsed:
    # Sidebar'ı tamamen gizlemek için CSS enjekte et
    st.markdown("<style>section[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

# --- OTURUM KONTROLÜ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Giriş sayfası (manuel olarak burada gösteriyoruz çünkü pages klasöründe çalışacak)
    st.title("🔐 DiploTrack Giriş")
    st.info("💡 Demo hesap: demo / demo123")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab1:
        with st.form("login_form"):
            uname = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş"):
                if auth.login_user(uname, pw):
                    st.success("Başarılı!")
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre.")
    with tab2:
        with st.form("register_form"):
            new_uname = st.text_input("Yeni Kullanıcı Adı")
            new_pw = st.text_input("Yeni Şifre", type="password")
            if st.form_submit_button("Kayıt Ol"):
                if auth.register_user(new_uname, new_pw):
                    st.success("Kayıt başarılı! Lütfen giriş yapın.")
                else:
                    st.error("Bu kullanıcı adı alınmış.")
    st.stop()

# --- GİRİŞ YAPILDIKTAN SONRA ---
# Sidebar düzenlemeleri
with st.sidebar:
    if st.button("🌓 Aydınlık/Karanlık"):
        st.session_state.dark_mode = not st.session_state.get("dark_mode", False)
        st.rerun()
    if st.button("⬅️ Sidebar'ı Gizle/Göster"):
        utils.toggle_sidebar()
        st.rerun()
    st.write(f"👤 {st.session_state.username}")
    st.write("---")
    if st.button("Çıkış Yap"):
        auth.logout()
        st.rerun()

# Streamlit'in pages/ klasöründeki sayfaları otomatik yönlendirmesi için boş bırakıyoruz.
# pages/ içindeki her dosya sırayla menüde görünecek.
# Kullanıcı girişi varsa buraya gelir, sayfa yüklenir.
