import os
import json
import cv2
import numpy as np
import face_recognition
import speech_recognition as sr
import asyncio
from edge_tts import Communicate
from dotenv import dotenv_values

# === Load environment variables ===
env_vars = dotenv_values(".env")
JARVIS_VOICE_NAME = env_vars.get("AssistantVoice")

# === Directories ===
faces_dir = "UserData/faces"
passwords_dir = "UserData/passwords"
usernames_file = "UserData/usernames.json"
active_user_file = "UserData/active_user.json"
os.makedirs(faces_dir, exist_ok=True)
os.makedirs(passwords_dir, exist_ok=True)
os.makedirs("UserData", exist_ok=True)

# === TTS Function using edge-tts ===
async def speak_async(text):
    try:
        communicate = Communicate(text=text, voice=JARVIS_VOICE_NAME)
        await communicate.play()
    except Exception as e:
        print(f"⚠️ TTS error: {e}")

def speak(text):
    asyncio.run(speak_async(text))

# === Active User Management ===
def set_active_user(username):
    with open(active_user_file, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f)

def get_active_user():
    try:
        with open(active_user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("username")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def clear_active_user():
    if os.path.exists(active_user_file):
        os.remove(active_user_file)

# === User Registration ===
def register_user(username):
    if os.path.exists(usernames_file):
        with open(usernames_file, 'r') as f:
            try:
                usernames = json.load(f)
            except json.JSONDecodeError:
                usernames = []
    else:
        usernames = []

    if username in usernames:
        print("⚠️ Username already exists.")
        return False

    # === Capture face ===
    cap = cv2.VideoCapture(0)
    print("📸 Capturing face. Please look at the camera...")

    face_encoding = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, boxes)

        if encodings:
            face_encoding = encodings[0]
            np.save(f"{faces_dir}/{username}_face.npy", face_encoding)
            print("✅ Face captured successfully.")
            break

        cv2.imshow("Capturing Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("❌ Face capture canceled.")
            cap.release()
            cv2.destroyAllWindows()
            return False

    cap.release()
    cv2.destroyAllWindows()

    # === Prompt and record voice password (with retry loop) ===
    recognizer = sr.Recognizer()
    attempt = 0
    max_attempts = 3
    password = None

    while attempt < max_attempts:
        print("🎤 Prompting for voice password...")
        speak("Say your password now")

        with sr.Microphone() as source:
            recognizer.energy_threshold = 300
            recognizer.pause_threshold = 1.0
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5)
                password = recognizer.recognize_google(audio).strip()
                print(f"✅ Password captured: {password}")
                break
            except sr.WaitTimeoutError:
                print("⏰ Timeout: No voice detected.")
            except sr.UnknownValueError:
                print("❌ Could not understand your speech.")
            except sr.RequestError:
                print("❌ Speech recognition service error.")
        attempt += 1
        speak("Please try again")

    if not password:
        print("❌ Failed to capture valid voice password.")
        return False

    with open(f"{passwords_dir}/{username}_password.txt", "w") as f:
        f.write(password)

    usernames.append(username)
    with open(usernames_file, 'w') as f:
        json.dump(usernames, f)

    print("🎉 User registration complete.")
    return True

# === Face Verification ===
def verify_face(username):
    face_path = f"{faces_dir}/{username}_face.npy"
    if not os.path.exists(face_path):
        print("❌ No face data found for this user.")
        return False

    known_encoding = np.load(face_path)
    cap = cv2.VideoCapture(0)
    print("🔍 Verifying face...")

    match = False
    for _ in range(50):
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, boxes)

        if encodings:
            distance = face_recognition.face_distance([known_encoding], encodings[0])[0]
            if distance < 0.5:
                match = True
                print("✅ Face verified.")
                break

        cv2.imshow("Verifying Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return match

# === Voice Password Verification ===
def verify_password(username):
    password_file = f"{passwords_dir}/{username}_password.txt"
    if not os.path.exists(password_file):
        print("❌ No password found for this user.")
        return False

    with open(password_file, "r") as f:
        stored_password = f.read().strip()

    recognizer = sr.Recognizer()
    attempt = 0
    max_attempts = 3

    while attempt < max_attempts:
        speak("Please say your password")
        with sr.Microphone() as source:
            recognizer.energy_threshold = 300
            recognizer.pause_threshold = 1.0
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5)
                spoken_password = recognizer.recognize_google(audio).strip()
                print(f"🔐 You said: {spoken_password}")

                if spoken_password.lower() == stored_password.lower():
                    print("✅ Password matched.")
                    return True
                else:
                    print("❌ Incorrect password.")
            except sr.WaitTimeoutError:
                print("⏰ Timeout: No voice detected.")
            except sr.UnknownValueError:
                print("❌ Could not understand speech.")
            except sr.RequestError:
                print("❌ Speech recognition error.")
        attempt += 1
        speak("Try again")

    print("❌ Failed password verification.")
    return False

# === Full Verification Flow ===
def verify_user(username):
    if verify_face(username) and verify_password(username):
        set_active_user(username)
        print(f"🔓 User '{username}' logged in and set as active user.")
        return True
    else:
        print("❌ Verification failed.")
        return False

# === Load usernames ===
def load_usernames():
    if not os.path.exists(usernames_file):
        return []
    with open(usernames_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
