import hashlib
import datetime
import streamlit as st
from . import db

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password):
    users = db.load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "tier": "free",
        "usage_this_month": 0,
        "last_active_month": datetime.date.today().strftime("%Y-%m"),
        "created_at": str(datetime.datetime.now()),
        "badges": []
    }
    db.save_users(users)
    return True

def login_user(username, password):
    user = db.get_user(username)
    if user and user["password"] == hash_password(password):
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_data"] = user
        current_month = datetime.date.today().strftime("%Y-%m")
        if user.get("last_active_month") != current_month:
            db.update_user(username, {"usage_this_month": 0, "last_active_month": current_month})
            st.session_state["user_data"]["usage_this_month"] = 0
        return True
    return False

def create_default_user():
    users = db.load_users()
    if not users:
        users["demo"] = {
            "password": hash_password("demo123"),
            "tier": "free",
            "usage_this_month": 0,
            "last_active_month": datetime.date.today().strftime("%Y-%m"),
            "created_at": str(datetime.datetime.now()),
            "badges": []
        }
        db.save_users(users)

def logout():
    for key in ["logged_in", "username", "user_data"]:
        if key in st.session_state:
            del st.session_state[key]
