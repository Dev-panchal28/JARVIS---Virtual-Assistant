from googlesearch import search
from groq import Groq
from json import load, dump
from datetime import datetime
from dotenv import dotenv_values
import os

# === Load environment variables ===
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# === Groq Client ===
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

# === Load and save chat history ===
def load_chat_history():
    path = ensure_chat_file()
    try:
        with open(path, "r") as f:
            return load(f)
    except:
        return []

def save_chat_history(history):
    path = get_chat_file_path()
    with open(path, "w") as f:
        dump(history, f, indent=4)

# === System prompt ===
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***
"""

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# === Google Search Results ===
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

# === Real-time info for model context ===
def Information():
    now = datetime.now()
    return (
        f"Use This Real-time Information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

# === Answer cleanup ===
def AnswerModifier(Answer):
    return '\n'.join(line for line in Answer.split('\n') if line.strip())

# === Main function ===
def RealtimeSearchEngine(prompt):
    global SystemChatBot

    messages = load_chat_history()
    messages.append({"role": "user", "content": prompt})

    # Add temporary system message with Google search results
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("<s>", "")
        messages.append({"role": "assistant", "content": Answer})
        save_chat_history(messages)

        return AnswerModifier(Answer)
    except Exception as e:
        return f"Error: {e}"
    finally:
        SystemChatBot.pop()  # Remove temporary system content

# === CLI testing ===
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
