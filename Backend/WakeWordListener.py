# --- WakeWordListener.py ---
import speech_recognition as sr
from time import sleep
import pygame
from Frontend.GUI import (
    SetAssistantStatus,
    ShowTextToScreen,
    texttospeech,
    GetMicrophoneStatus,
    GetWakeTriggerEnabled
    
)

wake_word_enabled = True

def toggle_wake_word_listening(enable: bool):
    global wake_word_enabled
    wake_word_enabled = enable

def is_wake_word_enabled():
    return wake_word_enabled

'''
def play_wake_up_sound():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("Data/wake_up.mp3")  # Update this path if needed
        pygame.mixer.music.play()
    except Exception as e:
        print(f"[WakeWord] Failed to play sound: {e}")
'''

def listen_for_wake_word(callback=None, wake_words=None):
    if wake_words is None:
        wake_words = ["hello"]

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        if not GetWakeTriggerEnabled() or not wake_word_enabled or GetMicrophoneStatus().lower() == "true":
            sleep(0.5)
            continue

        try:
            print("[WakeWord] Listening for wake word...")
            with mic as source:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)

            query = recognizer.recognize_google(audio).lower()
            print(f"[WakeWord] Heard: {query}")

            if "stop listening" in query:
                ShowTextToScreen("Wake word disabled.")
                SetAssistantStatus("Wake Word Disabled")
                texttospeech("Okay, I will stop listening now.")
                toggle_wake_word_listening(False)
                continue
                

            if any(wake_word in query for wake_word in wake_words):
                #play_wake_up_sound()  # Play wake-up chime
                ShowTextToScreen("Hello!! How can I assist you?")
                SetAssistantStatus("Waking up...")
                texttospeech("Hello!! How can I assist you?")
                if callback:
                    callback()  # Notify main.py
                sleep(0.5)

        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"[WakeWord] API error: {e}")
            continue
        except Exception as e:
            print(f"[WakeWord] Exception: {e}")
            continue
