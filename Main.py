from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
    GetWakeTriggerEnabled
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.WakeWordListener import listen_for_wake_word
from Backend.laptop import perform_laptop_command
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import threading
import json
import os
import re
import pygame

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")

# Global state
mic_triggered_by_wakeword = False
execution_lock = threading.Lock()
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""

# -------------------------------------------
# Utility Functions
# -------------------------------------------

def GetCurrentChatLogPath():
    path = "UserData/active_user.json"
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                username = data.get("username", "").strip()
                if username:
                    return f"Data/ChatLog_{username}.json"
        except Exception:
            pass
    return "Data/ChatLog.json"

def sanitize_for_tts(text):
    return re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)

def ShowDefaultChatIfNoChats():
    file_path = GetCurrentChatLogPath()
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 5:
        with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    path = GetCurrentChatLogPath()
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted += f"{Username} : {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted += f"{Assistantname} : {entry['content']}\n"
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        data = file.read()
    if data.strip():
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(data)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

# -------------------------------------------
# AI Logic
# -------------------------------------------

def MainExecution():
    global mic_triggered_by_wakeword

    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")

    if mic_triggered_by_wakeword and "stop listening" in Query.lower():
        mic_triggered_by_wakeword = False
        SetMicrophoneStatus("False")
        SetAssistantStatus("Available...")
        TextToSpeech("Wake word listening stopped. You can manually turn on the microphone anytime.")
        return

    # Check for laptop command
    if any(keyword in Query.lower() for keyword in [
        "file", "folder", "shutdown", "restart", "bluetooth", "wifi", "wi-fi",
        "brightness", "volume", "system info", "laptop info", "create", "make", "delete", "remove"
    ]):
        result = perform_laptop_command(Query)
        ShowTextToScreen(f"{Assistantname} : {result}")
        SetAssistantStatus("Answering...")
        TextToSpeech(sanitize_for_tts(result))
        return

    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    print(f"\nDecision : {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)
    Merged_query = " and ".join([" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")])

    for q in Decision:
        if "generate " in q:
            # Check for active user
            try:
                with open("UserData/active_user.json", "r", encoding="utf-8") as f:
                    user = json.load(f).get("username", "").strip()
            except Exception:
                user = ""

            if not user:
                msg = "Please login to use image generation."
                ShowTextToScreen(f"{Assistantname} : {msg}")
                SetAssistantStatus("Answering...")
                TextToSpeech(sanitize_for_tts(msg))
                return

            with open("Frontend/Files/ImageGeneration.data", "w") as file:
                file.write(f"{q},True")
            msg = "Generating images. Please wait..."
            ShowTextToScreen(f"{Assistantname} : {msg}")
            SetAssistantStatus("Answering...")
            TextToSpeech(sanitize_for_tts(msg))
            return


    for q in Decision:
        if any(q.startswith(func) for func in Functions):
            run(Automation(Decision))
            return

    Answer = ""

    if G or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
    else:
        for q in Decision:
            if "general" in q:
                QueryFinal = q.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal), chatlog_path=GetCurrentChatLogPath())
                break
            elif "realtime" in q:
                QueryFinal = q.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                break
            elif "exit" in q or "bye" in q:
                Answer = ChatBot(QueryModifier("Okay, Bye!"), chatlog_path=GetCurrentChatLogPath())
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(sanitize_for_tts(Answer))
                os._exit(0)

    if Answer:
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(sanitize_for_tts(Answer))

# -------------------------------------------
# Wake Word Callback
# -------------------------------------------

def on_wake_word_detected():
    global mic_triggered_by_wakeword
    mic_triggered_by_wakeword = True
    SetMicrophoneStatus("True")

# -------------------------------------------
# Threads
# -------------------------------------------

def MicListenerThread():
    global mic_triggered_by_wakeword
    while True:
        if GetMicrophoneStatus().lower() == "true":
            if execution_lock.locked():
                sleep(0.1)
                continue
            SetAssistantStatus("Listening...")
            with execution_lock:
                MainExecution()
                if mic_triggered_by_wakeword:
                    SetMicrophoneStatus("False")
                    mic_triggered_by_wakeword = False
        else:
            if "Available..." not in GetAssistantStatus():
                SetAssistantStatus("Available...")
            sleep(0.1)

def GUIThread():
    GraphicalUserInterface()

def WakeWordThread():
    listen_for_wake_word(callback=on_wake_word_detected)

# -------------------------------------------
# Startup
# -------------------------------------------

if __name__ == "__main__":
    InitialExecution()

    threading.Thread(target=lambda: os.system("python Backend/ImageGeneration.py"), daemon=True).start()
    threading.Thread(target=MicListenerThread, daemon=True).start()
    threading.Thread(target=WakeWordThread, daemon=True).start()

    GUIThread()
