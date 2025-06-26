# === Import Required Libraries ===
from groq import Groq                     # Groq API client for LLM-based responses
from json import load, dump              # JSON handling for chat logs
import datetime                          # For real-time date and time
from dotenv import dotenv_values         # Load environment variables from .env

# === Load Environment Variables ===
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# === Initialize Groq Client ===
client = Groq(api_key=GroqAPIKey)

# === Global Chat Context ===
messages = []

# === System Prompt for the Assistant ===
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# === Groq Prompt Structure ===
SystemChatBot = [{"role": "system", "content": System}]

# === Load Chat History (if exists) ===
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# === Real-Time Info Helper ===
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# === Answer Formatter ===
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# === Main Chat Function ===
def ChatBot(Query):
    try:
        # Load existing chat history
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Add user query to the conversation
        messages.append({"role": "user", "content": f"{Query}"})

        # Generate AI response using Groq
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""

        # Read the streamed response
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")  # Remove stop token if present

        # Save assistant response
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log to file
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)  # Retry once

# === Manual Test Runner ===
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
