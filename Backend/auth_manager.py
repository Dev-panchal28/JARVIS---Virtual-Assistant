# ============================================
# File: auth_manager.py
# Purpose: Handles face + voice-based signup/login authentication
# ============================================

import os
import json
import cv2
import numpy as np
import face_recognition
import speech_recognition as sr
import asyncio
import pygame
from edge_tts import Communicate
from dotenv import dotenv_values

# === Load environment variables ===
env_vars = dotenv_values(".env")
JARVIS_VOICE_NAME = env_vars.get("AssistantVoice")

# === Directory Setup ===
os.makedirs("UserData/faces", exist_ok=True)
os.makedirs("UserData/passwords", exist_ok=True)
os.makedirs("UserData", exist_ok=True)
os.makedirs("Data", exist_ok=True)

# === File Paths ===
FACES_DIR = "UserData/faces"
PASSWORDS_DIR = "UserData/passwords"
USERNAMES_FILE = "UserData/usernames.json"
ACTIVE_USER_FILE = "UserData/active_user.json"

# ============================================
# Section: Text-to-Speech Handling
# ============================================

async def generate_tts(text: str, filepath="Data/speech.mp3", voice=JARVIS_VOICE_NAME):
    """Generate TTS audio using edge-tts and save to file."""
    try:
        communicate = Communicate(text=text, voice=voice)
        await communicate.save(filepath)
    except Exception as e:
        print(f"⚠️ TTS generation error: {e}")

def play_audio(filepath):
    """Play the given audio file using pygame."""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"⚠️ Playback error: {e}")
    finally:
        pygame.mixer.quit()

def speak(text: str):
    """Convert text to speech and play it along with a beep sound."""
    asyncio.run(generate_tts(text))
    play_audio("Data/speech.mp3")
    play_audio("Data/beep.mp3")

# ============================================
# Section: Active User Management
# ============================================

def set_active_user(username):
    with open(ACTIVE_USER_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f)

def get_active_user():
    try:
        with open(ACTIVE_USER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("username") if data.get("username") else None
    except:
        return None

def clear_active_user():
    with open(ACTIVE_USER_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": None}, f)

# ============================================
# Section: User Storage & Retrieval
# ============================================

def load_usernames():
    if not os.path.exists(USERNAMES_FILE):
        return []
    try:
        with open(USERNAMES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_username(username):
    usernames = load_usernames()
    usernames.append(username)
    with open(USERNAMES_FILE, "w") as f:
        json.dump(usernames, f)

# ============================================
# Section: Signup Process
# ============================================

def signup_flow(username):
    if username in load_usernames():
        print("⚠️ Username already exists.")
        return False

    # === Step 1: Capture Face ===
    cap = cv2.VideoCapture(0)
    print("📸 Capturing face. Look at the camera...")
    face_encoding = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)

        if encodings:
            face_encoding = encodings[0]
            print("✅ Face captured.")
            break

        cv2.imshow("Capturing Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("❌ Cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return False

    cap.release()
    cv2.destroyAllWindows()

    # === Step 2: Capture Voice Password ===
    recognizer = sr.Recognizer()
    password = None
    for attempt in range(3):
        speak("Say your password after beep")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5)
                password = recognizer.recognize_google(audio).strip()
                print(f"✅ Password captured: {password}")
                break
            except:
                print("❌ Try again.")
                speak("Please try again")

    if not password:
        print("❌ Failed to capture password.")
        return False

    # === Save Face + Voice Data ===
    np.save(f"{FACES_DIR}/{username}_face.npy", face_encoding)
    with open(f"{PASSWORDS_DIR}/{username}_password.txt", "w") as f:
        f.write(password)
    save_username(username)

    print("🎉 Signup successful.")
    return True

# ============================================
# Section: Login Process
# ============================================

def login_flow(username):
    active = get_active_user()
    if active:
        print(f"⚠️ Another user '{active}' is already logged in.")
        return False

    if username not in load_usernames():
        print("❌ Username not found.")
        return False

    face_path = f"{FACES_DIR}/{username}_face.npy"
    pass_path = f"{PASSWORDS_DIR}/{username}_password.txt"

    if not os.path.exists(face_path) or not os.path.exists(pass_path):
        print("❌ Missing data.")
        return False

    # === Step 1: Verify Face ===
    known_encoding = np.load(face_path)
    cap = cv2.VideoCapture(0)
    print("🔍 Verifying face...")
    match = False

    for _ in range(50):
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)

        if encodings and face_recognition.face_distance([known_encoding], encodings[0])[0] < 0.5:
            match = True
            print("✅ Face verified.")
            break

        cv2.imshow("Verifying Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not match:
        print("❌ Face mismatch.")
        return False

    # === Step 2: Verify Voice Password ===
    with open(pass_path, "r") as f:
        stored_password = f.read().strip()

    recognizer = sr.Recognizer()
    for attempt in range(3):
        speak("Please say your password after beep")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5)
                spoken = recognizer.recognize_google(audio).strip()
                print(f"🔐 You said: {spoken}")
                if spoken.lower() == stored_password.lower():
                    print("✅ Password matched.")
                    set_active_user(username)
                    return True
            except:
                print("❌ Try again.")
                speak("Try again")

    print("❌ Voice verification failed.")
    return False

# ============================================
# Section: Logout
# ============================================

def logout_flow():
    if get_active_user():
        clear_active_user()
        print("👋 Logged out successfully.")
        return True
    else:
        print("⚠️ No active user to log out.")
        return False
