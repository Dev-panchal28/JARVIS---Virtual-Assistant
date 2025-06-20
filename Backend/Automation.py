# Import required libraries
from AppOpener import close, give_appnames, open as appopen # Import functions to open and close apps.
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import Groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import keyboard  # Import keyboard for keyboard-related actions.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.
import re

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key.

# Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgKELc", "LTKOO sY7ric", "Z0LCW", "gsrt vk_bk FzWSb YwPhnf", "pcIqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "O5uR6d LTKOO", "vIzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe",
           "LWkFke", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'


client = Groq(api_key=GroqAPIKey)


professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]


messages = []


SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]


def GoogleSearch(Topic):
    search(Topic)
    return True


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
    
    Topic: str = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)


    with open(rf"Data\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()
    
    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt")
    return True



def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app):
    try:
        available_apps = give_appnames()
        
        if app.lower() not in available_apps:
            print(f"'{app}' is not a recognized application. Opening in browser instead...")
            webbrowser.open(f"https://www.{app.lower()}.com")  # Open the website instead
            return
        
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"Opening {app}...")

    except Exception as e:
        print(f"Error opening {app}: {e}")

def extract_links(html):
    """Extracts only valid URLs from the HTML content."""
    links = re.findall(r'https?://[^\s"\'>]+', html)  # Excludes trailing unwanted characters
    return links

# Simulated HTML content (replace with actual source)
html = "<a href='https://example.com'>Example</a>"

# Extract links safely
links = extract_links(html)

if links:
    link = links[0]  # Safely access first link
    #print(f"Extracted link: {link}")
else:
    print("No valid links found in the given HTML.")


def CloseApp(app):

    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False


def System(command):


    def mute():
        keyboard.press_and_release("volume mute")
    

    def unmute():
        keyboard.press_and_release("volume unmute")
    

    def volume_up():
        keyboard.press_and_release("volume up")
    

    def volume_down():
        keyboard.press_and_release("volume down")
    

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    
    return True


async def TranslateAndExecute(commands: list[str]):

    funcs = []

    for command in commands:

        if command.startswith("open "):

            if "open it" in command:
                pass

            if "open file" == command:
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        
        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        
        else:
            print(f"No Function Found. For {command}")
    
    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result


async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):
        pass

    return True


        

