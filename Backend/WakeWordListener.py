# === WakeWordListener.py ===

# === Imports ===
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

# === Wake Word Listening State ===
wake_word_enabled = True  # Global flag to control wake word behavior

def toggle_wake_word_listening(enable: bool):
    """Enable or disable the wake word listener."""
    global wake_word_enabled
    wake_word_enabled = enable

def is_wake_word_enabled():
    """Return current state of wake word listener."""
    return wake_word_enabled

# === Wake Word Sound (Optional) ===
# def play_wake_up_sound():
#     """Play a wake-up chime (currently unused)."""
#     try:
#         pygame.mixer.init()
#         pygame.mixer.music.load("Data/wake_up.mp3")
#         pygame.mixer.music.play()
#     except Exception as e:
#         print(f"[WakeWord] Failed to play sound: {e}")

# === Main Wake Word Listener Loop ===
def listen_for_wake_word(callback=None, wake_words=None):
    """Continuously listen for the wake word and trigger a callback."""
    if wake_words is None:
        wake_words = ["hello"]

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    # Adjust mic for ambient noise
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        # Respect toggles from GUI or internal flags
        if not GetWakeTriggerEnabled() or not wake_word_enabled or GetMicrophoneStatus().lower() == "true":
            sleep(0.5)
            continue

        try:
            print("[WakeWord] Listening for wake word...")
            with mic as source:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)

            query = recognizer.recognize_google(audio).lower()
            print(f"[WakeWord] Heard: {query}")

            # Command to stop listening
            if "stop listening" in query:
                ShowTextToScreen("Wake word disabled.")
                SetAssistantStatus("Wake Word Disabled")
                texttospeech("Okay, I will stop listening now.")
                toggle_wake_word_listening(False)
                continue

            # Wake word matched
            if any(wake_word in query for wake_word in wake_words):
                # play_wake_up_sound()  # Optionally play chime
                ShowTextToScreen("Hello!! How can I assist you?")
                SetAssistantStatus("Waking up...")
                texttospeech("Hello!! How can I assist you?")
                if callback:
                    callback()  # Trigger callback to Main.py
                sleep(0.5)

        except sr.UnknownValueError:
            continue  # Could not understand audio
        except sr.RequestError as e:
            print(f"[WakeWord] API error: {e}")
            continue
        except Exception as e:
            print(f"[WakeWord] Exception: {e}")
            continue
