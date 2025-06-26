# === Imports ===
from googlesearch import search  # For Google-like search results
from groq import Groq            # LLaMA-3 chat client via Groq API
from json import load, dump      # For reading/writing chat log JSON
import datetime                  # For real-time date/time info
from dotenv import dotenv_values # To load environment variables from .env

# === Load Environment Variables ===
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# === Initialize Groq Client ===
client = Groq(api_key=GroqAPIKey)

# === System Prompt for the Assistant ===
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# === Initialize Chat History File ===
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# === Google Search Helper ===
def GoogleSearch(query):
    """Perform a Google-style search and return top 5 result titles + descriptions."""
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

# === Answer Cleaner ===
def AnswerModifier(Answer):
    """Remove empty lines from the assistant's response."""
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# === Default ChatBot Conversation Bootstrap ===
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# === Real-time Information Generator ===
def Information():
    """Return current date, time, and day in a formatted string."""
    now = datetime.datetime.now()
    return (
        "Use This Real-time Information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

# === Main Function: AI with Web Search & Real-time Data ===
def RealtimeSearchEngine(prompt):
    """Main function that combines Google search + real-time data + Groq AI reply."""
    global SystemChatBot, messages

    # Load chat history
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    
    # Append new user prompt
    messages.append({"role": "user", "content": prompt})
    
    # Temporarily add search result context
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Generate AI response using Groq
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    # Collect the streamed reply
    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Clean and append assistant's response
    Answer = Answer.strip().replace("<s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save updated chat log
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)
    
    # Remove temporary Google search system message
    SystemChatBot.pop()

    # Return clean reply
    return AnswerModifier(Answer)

# === Entry Point for CLI Testing ===
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
