from groq import Groq
from json import load, dump
from datetime import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# === Paths ===
global_chat_path = r"Data\ChatLog.json"
user_chat_dir = "UserData/chat"
active_user_file = "UserData/active_user.json"

os.makedirs("Data", exist_ok=True)
os.makedirs(user_chat_dir, exist_ok=True)

# === Get active user ===
def get_active_username():
    if not os.path.exists(active_user_file):
        return None
    try:
        with open(active_user_file, "r") as f:
            data = load(f)
            return data.get("username")
    except Exception:
        return None

# === Get correct chat file ===
def get_chat_file_path():
    username = get_active_username()
    if username:
        return os.path.join(user_chat_dir, f"{username}_history.json")
    return global_chat_path

# === Ensure chat file is valid ===
def ensure_chat_file():
    path = get_chat_file_path()
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as f:
            dump([], f)
    return path

# === Load chat history ===
def load_chat_history():
    path = ensure_chat_file()
    try:
        with open(path, "r") as f:
            return load(f)
    except Exception:
        return []

# === Save chat history ===
def save_chat_history(history):
    path = get_chat_file_path()
    with open(path, "w") as f:
        dump(history, f, indent=4)

# === System prompt setup ===
SystemPrompt = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
SystemChatBot = [{"role": "system", "content": SystemPrompt}]

# === Get real-time info ===
def RealtimeInformation():
    now = datetime.now()
    return (
        f"Please use this real-time information if needed,\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes :{now.strftime('%S')} seconds.\n"
    )

# === Clean assistant output ===
def AnswerModifier(answer):
    lines = answer.split('\n')
    return '\n'.join(line for line in lines if line.strip())

# === Main chatbot function ===
def ChatBot(query):
    try:
        messages = load_chat_history()
    except Exception:
        messages = []

    messages.append({"role": "user", "content": query})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})
        save_chat_history(messages)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."

# === CLI Usage ===
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
