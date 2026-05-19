import streamlit as st
from modules import auth, db, utils

st.set_page_config(page_title="DiploTrack", page_icon="🌐", layout="wide")
utils.apply_theme()
db.init_db()

# Otomatik demo ve öğretmen hesabı oluştur
auth.create_default_user()

# Oturum süresi kontrolü
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Giriş / Kayıt / Şifre Sıfırlama sayfası
    page = st.radio("", ["Giriş Yap", "Kayıt Ol", "Şifremi Unuttum"], horizontal=True)

    if page == "Giriş Yap":
        st.title("🔐 Giriş Yap")
        uname = st.text_input("Kullanıcı Adı")
        pw = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            if auth.login_user(uname, pw):
                st.success("Başarılı!")
                st.rerun()
            else:
                st.error("Hatalı giriş.")

    elif page == "Kayıt Ol":
        st.title("📝 Kayıt Ol")
        new_uname = st.text_input("Kullanıcı Adı")
        new_pw = st.text_input("Şifre", type="password")
        sq = st.selectbox("Güvenlik Sorusu", ["Evcil hayvanınızın adı?", "Doğduğunuz şehir?"])
        sa = st.text_input("Cevap")
        role = st.selectbox("Rol", ["student", "teacher"])
        if st.button("Kayıt Ol"):
            if auth.register_user(new_uname, new_pw, sq, sa, role):
                st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
            else:
                st.error("Kullanıcı adı alınmış.")

    else:  # Şifremi Unuttum
        st.title("🔑 Şifre Sıfırla")
        uname = st.text_input("Kullanıcı Adınız")
        user = db.get_user(uname)
        if user:
            st.write(f"Güvenlik Sorunuz: {user['security_question']}")
            answer = st.text_input("Cevap")
            new_pw = st.text_input("Yeni Şifre", type="password")
            if st.button("Şifreyi Sıfırla"):
                if auth.verify_security_answer(uname, answer):
                    auth.reset_password(uname, new_pw)
                    st.success("Şifre sıfırlandı! Giriş yapabilirsiniz.")
                else:
                    st.error("Cevap yanlış.")
        else:
            st.error("Kullanıcı bulunamadı.")
    st.stop()

# Giriş yapıldıysa sidebar
utils.check_session_timeout()
with st.sidebar:
    st.write(f"👤 {st.session_state['username']} ({st.session_state['user_data']['role']})")
    if st.button("🌓 Tema"):
        st.session_state.dark_mode = not st.session_state.get("dark_mode", False)
        st.rerun()
    st.write("---")
    if st.button("Çıkış Yap"):
        auth.logout()
        st.rerun()

# pages/ otomatik yönlendirilir, bir şey yapmaya gerek yok.
