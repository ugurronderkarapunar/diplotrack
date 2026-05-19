import json
import datetime
from pathlib import Path

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
SIMULATIONS_DIR = DATA_DIR / "simulations"

def init_data():
    DATA_DIR.mkdir(exist_ok=True)
    SIMULATIONS_DIR.mkdir(exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_user(username):
    users = load_users()
    return users.get(username)

def update_user(username, updates):
    users = load_users()
    users[username].update(updates)
    save_users(users)

def get_user_sim_dir(username):
    d = SIMULATIONS_DIR / username
    d.mkdir(exist_ok=True)
    return d

def save_simulation(username, sim_data):
    d = get_user_sim_dir(username)
    sim_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filepath = d / f"{sim_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sim_data, f, indent=2, ensure_ascii=False)
    return filepath

def load_user_simulations(username):
    d = get_user_sim_dir(username)
    sims = []
    for f in sorted(d.glob("*.json"), reverse=True):
        with open(f, "r", encoding="utf-8") as fp:
            sims.append(json.load(fp))
    return sims
