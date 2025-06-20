# File: SpeechManager.py

import threading
import pygame
import os
import asyncio
import time
import speech_recognition as sr
from edge_tts import Communicate

# Global control variables
tts_thread = None
interrupt_thread = None
is_speaking = False
audio_file_path = "Data/output.mp3"

# Initialize Pygame mixer
pygame.mixer.init()

def generate_tts_audio(text):
    async def save_audio():
        communicate = Communicate(text, "en-CA-LiamNeural")
        await communicate.save(audio_file_path)

    asyncio.run(save_audio())

def play_audio():
    global is_speaking
    try:
        pygame.mixer.music.load(audio_file_path)
        pygame.mixer.music.play()
        is_speaking = True
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print(f"[SpeechManager] Audio playback failed: {e}")
    finally:
        is_speaking = False

def speak(text):
    global tts_thread, interrupt_thread

    stop_speech()  # Stop any current speech

    generate_tts_audio(text)

    # Start TTS thread
    tts_thread = threading.Thread(target=play_audio)
    tts_thread.start()

    # Start interruption listener
    interrupt_thread = threading.Thread(target=listen_for_interruption)
    interrupt_thread.start()

def stop_speech():
    global is_speaking
    if is_speaking:
        pygame.mixer.music.stop()
        is_speaking = False

def listen_for_interruption(trigger_word="cut it"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("[SpeechManager] Listening for interruption keyword...")

        while is_speaking:
            try:
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)
                user_input = recognizer.recognize_google(audio)
                print(f"[SpeechManager] Heard: {user_input}")

                if trigger_word.lower() in user_input.lower():
                    print("[SpeechManager] Interruption detected!")
                    stop_speech()
                    break

            except sr.UnknownValueError:
                continue
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"[SpeechManager] Error in interruption detection: {e}")
                break

