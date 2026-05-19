import hashlib
import datetime
import streamlit as st
from . import db

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password, security_q, security_a, role="student"):
    if db.get_user(username):
        return False
    now = datetime.datetime.now().isoformat()
    data = {
        "username": username,
        "password": hash_password(password),
        "tier": "free",
        "role": role,
        "usage_this_month": 0,
        "credits": 0,
        "last_active_month": datetime.date.today().strftime("%Y-%m"),
        "security_question": security_q,
        "security_answer": hash_password(security_a.lower()),
        "created_at": now,
        "badges": "[]"
    }
    db.save_user(username, data)
    db.log_action(username, "register")
    return True

def login_user(username, password):
    user = db.get_user(username)
    if user and user["password"] == hash_password(password):
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_data"] = user
        current_month = datetime.date.today().strftime("%Y-%m")
        if user["last_active_month"] != current_month:
            db.update_user(username, {"usage_this_month": 0, "last_active_month": current_month})
            user["usage_this_month"] = 0
            st.session_state["user_data"]["usage_this_month"] = 0
        db.log_action(username, "login")
        return True
    return False

def verify_security_answer(username, answer):
    user = db.get_user(username)
    if not user:
        return False
    return user["security_answer"] == hash_password(answer.lower())

def reset_password(username, new_password):
    db.update_user(username, {"password": hash_password(new_password)})
    db.log_action(username, "password_reset")

def create_default_user():
    if not db.get_user("demo"):
        register_user("demo", "demo123", "Evcil hayvanınızın adı?", "kedi")
    # Opsiyonel öğretmen hesabı
    if not db.get_user("ogretmen"):
        register_user("ogretmen", "ogretmen123", "En sevdiğiniz ders?", "tarih", role="teacher")

def logout():
    for key in ["logged_in", "username", "user_data"]:
        if key in st.session_state:
            del st.session_state[key]
