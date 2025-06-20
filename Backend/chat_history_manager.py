import os
import json

# === Paths ===
global_chat_file = "Data/ChatLog.json"
chat_dir = "UserData/chat"
active_user_file = "UserData/active_user.json"

os.makedirs("UserData", exist_ok=True)
os.makedirs(chat_dir, exist_ok=True)

# === Helper: Get active username ===
def get_active_username():
    if not os.path.exists(active_user_file):
        return None
    try:
        with open(active_user_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("username")
    except json.JSONDecodeError:
        return None

# === Helper: Get correct history path ===
def get_history_file_path():
    username = get_active_username()
    if username:
        return os.path.join(chat_dir, f"{username}_history.json")
    else:
        return global_chat_file

# === Get chat history ===
def get_chat_history():
    path = get_history_file_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

# === Save new message ===
def save_message(role, message):
    path = get_history_file_path()
    history = get_chat_history()
    history.append({"role": role, "message": message})
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

# === Clear history ===
def clear_chat_history():
    path = get_history_file_path()
    if os.path.exists(path):
        os.remove(path)
        print("🧹 Chat history cleared.")
