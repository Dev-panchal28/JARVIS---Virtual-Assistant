# === Import Required Libraries ===
from AppOpener import close, give_appnames, open as appopen  # App control
from webbrowser import open as webopen                        # Open URLs
from pywhatkit import search, playonyt                        # Google & YouTube utilities
from dotenv import dotenv_values                              # Load environment variables
from bs4 import BeautifulSoup                                 # Parse HTML (optional)
from rich import print                                        # Pretty print
from groq import Groq                                         # LLM API
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import re

# === Load API Keys from .env ===
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# === Define default parsing classes for fallback web scraping ===
classes = [
    "zCubwf", "hgKELc", "LTKOO sY7ric", "Z0LCW", "gsrt vk_bk FzWSb YwPhnf", "pcIqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vIzY6d",
    "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt",
    "sXLaOe", "LWkFke", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# === Setup Groq AI Client ===
client = Groq(api_key=GroqAPIKey)

# === Default Assistant Messages ===
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []

# === Prompt configuration for AI Content Writing ===
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# === Google Search ===
def GoogleSearch(Topic):
    search(Topic)
    return True

# === Content Writing Feature ===
def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])
    
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    with open(rf"Data\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    
    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt")
    return True

# === YouTube Search & Playback ===
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

# === Application Management ===
def OpenApp(app):
    try:
        available_apps = give_appnames()
        
        if app.lower() not in available_apps:
            print(f"'{app}' is not a recognized application. Opening in browser instead...")
            webbrowser.open(f"https://www.{app.lower()}.com")  # Fallback to browser
            return
        
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"Opening {app}...")

    except Exception as e:
        print(f"Error opening {app}: {e}")

def CloseApp(app):
    if "chrome" in app:
        pass  # Skip closing Chrome via this logic
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

# === System Volume/Mute Controls ===
def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume unmute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")
    
    if command == "mute": mute()
    elif command == "unmute": unmute()
    elif command == "volume up": volume_up()
    elif command == "volume down": volume_down()
    
    return True

# === HTML Link Extractor Utility ===
def extract_links(html):
    """Extracts valid URLs from HTML content."""
    links = re.findall(r'https?://[^\s"\'>]+', html)
    return links

# === Command Translator ===
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open ") and "open it" not in command and "open file" != command:
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))

        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))

        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))

        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))

        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))

        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

        else:
            print(f"No Function Found for: {command}")
    
    results = await asyncio.gather(*funcs)

    for result in results:
        yield result if isinstance(result, str) else result

# === Automation Entry Point ===
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
