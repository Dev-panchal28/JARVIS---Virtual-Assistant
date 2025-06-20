import os
import shutil
import subprocess
import platform
import ctypes
import psutil
import socket
import getpass
import datetime
import re
import pyautogui
import pyttsx3
import speech_recognition as sr
from time import sleep
from pathlib import Path



# Optional: For volume control
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
except ImportError:
    AudioUtilities = None

DEFAULT_FOLDER_LOCATION = os.path.join(os.path.expanduser("~"), "Desktop")

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening for confirmation...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            response = recognizer.recognize_google(audio).lower()
            print(f"👂 You said: {response}")
            return response
        except sr.WaitTimeoutError:
            print("⌛ Timeout: No speech detected.")
            speak("I didn't hear anything. Please try again.")
            return "timeout"
        except sr.UnknownValueError:
            print("🤔 Could not understand audio.")
            speak("I could not understand. Please say yes or no.")
            return "unknown"
        except sr.RequestError as e:
            print(f"❌ API error: {e}")
            return f"error: {e}"


# ---------------------------
# Basic File/Folder Ops
# ---------------------------
def normalize_path(path):
    # Expand ~ and make absolute path
    return os.path.abspath(os.path.expanduser(path.strip().replace("\\", "/")))

def create_file(path):
    try:
        path = normalize_path(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write("")
        return f"✅ File created at {path}"
    except Exception as e:
        return f"❌ Failed to create file: {e}"

def delete_file(path):
    try:
        path = normalize_path(path)
        os.remove(path)
        return f"✅ File deleted at {path}"
    except Exception as e:
        return f"❌ Failed to delete file: {e}"

def create_folder(path):
    try:
        path = normalize_path(path)
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder created at {path}"
    except Exception as e:
        return f"❌ Failed to create folder: {e}"

def delete_folder(path):
    try:
        path = normalize_path(path)
        shutil.rmtree(path)
        return f"✅ Folder deleted at {path}"
    except Exception as e:
        return f"❌ Failed to delete folder: {e}"
    
def get_special_folder(folder_name):
    from pathlib import Path
    folder_name = folder_name.lower()
    if "desktop" in folder_name:
        return str(Path.home() / "Desktop")
    elif "documents" in folder_name or "document" in folder_name:
        return str(Path.home() / "Documents")
    elif "downloads" in folder_name:
        return str(Path.home() / "Downloads")
    elif "pictures" in folder_name:
        return str(Path.home() / "Pictures")
    elif "music" in folder_name:
        return str(Path.home() / "Music")
    elif "videos" in folder_name:
        return str(Path.home() / "Videos")
    else:
        return None



# ---------------------------
# System Control
# ---------------------------
def shutdown():
    try:
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        elif platform.system() in ["Linux", "Darwin"]:
            os.system("shutdown now")
        return "⚠️ Shutting down..."
    except Exception as e:
        return f"❌ Shutdown failed: {e}"

def restart():
    try:
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
        elif platform.system() in ["Linux", "Darwin"]:
            os.system("reboot")
        return "🔄 Restarting..."
    except Exception as e:
        return f"❌ Restart failed: {e}"

def bluetooth():
    sleep(2)
    coordinates = pyautogui.position()

    pyautogui.click(x=1812, y=20)
    sleep(2)
    pyautogui.click(x=1727, y=1055)
    sleep(2)
    pyautogui.click(x=1656, y=568)
    sleep(2)
    pyautogui.click(x=1439, y=1050)
    #sleep(2)

def wifi():
    sleep(2)
    coordinates = pyautogui.position()

    pyautogui.click(x=1812, y=20)
    sleep(2)
    pyautogui.click(x=1741, y=1046)
    sleep(2)
    pyautogui.click(x=1515, y=590)
    sleep(2)
    pyautogui.click(x=1439, y=1050)

# ---------------------------
# Device Controls
# ---------------------------
def set_brightness(level):
    if platform.system() == "Windows":
        try:
            import screen_brightness_control as sbc
            level = max(0, min(level, 100))  # Clamp between 0 and 100
            sbc.set_brightness(level)
            return f"🔆 Brightness set to {level}%"
        except Exception as e:
            return f"❌ Failed to set brightness: {e}"
    return "❌ Brightness control not supported on this OS."

def set_volume(level):
    if AudioUtilities is None:
        return "❌ Volume control not available. pycaw is not installed."
    try:
        level = max(0, min(level, 100))  # Clamp between 0 and 100
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"🔊 Volume set to {level}%"
    except Exception as e:
        return f"❌ Failed to set volume: {e}"


# ---------------------------
# Info
# ---------------------------
def get_system_info():
    try:
        info = {
            "Platform": platform.platform(),
            "OS": platform.system(),
            "Release": platform.release(),
            "CPU": platform.processor(),
            "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "Username": getpass.getuser(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    except Exception as e:
        return f"❌ Failed to fetch system info: {e}"

def normalize_folder_command(command: str) -> str:
    command = command.lower()

    # Fix common misphrases
    command = command.replace("name the", "named")
    command = command.replace("to indeed drive", "in e drive")
    command = command.replace("to c drive", "in c drive")
    command = command.replace("to d drive", "in d drive")
    command = command.replace("to e drive", "in e drive")
    command = command.replace("to", "in")  # generic fallback
    
    # Fix article misuse
    command = command.replace("the folder", "folder")

    return command

# ---------------------------
# Command Parser
# ---------------------------
def perform_laptop_command(command: str) -> str:
    command = command.lower()
    command = normalize_folder_command(command)  # ✅ Normalize phrasing early

    # Folder creation
    if any(phrase in command for phrase in ["make folder", "create folder", "new folder"]):
        # Extract folder name and path from natural language
        folder_match = re.search(
            r"create (?:a )?folder(?: named| called)? (?P<foldername>\w+)(?: in (?P<location>[a-zA-Z]:\\?.*))?",
            command
        )

        folder_name = folder_match.group("foldername").strip() if folder_match and folder_match.group("foldername") else "New Folder"
        raw_location = folder_match.group("location") if folder_match and folder_match.group("location") else ""

        # Try to identify drive manually like "in d drive in folder\subfolder"
        if not raw_location or not re.match(r"[a-zA-Z]:\\", raw_location):
            drive_match = re.search(r"([a-zA-Z])\s*drive(?:\| in)?\s*(.*)", command)
            if drive_match:
                drive_letter = drive_match.group(1).upper()
                sub_path = drive_match.group(2).strip().replace(" in ", "\\").replace(" ", "\\").strip("\\/")
                raw_location = f"{drive_letter}:\\" + sub_path
                if not os.path.exists(f"{drive_letter}:\\"):
                    return f"❌ Drive {drive_letter}:\\ does not exist."

        folder_path = os.path.join(raw_location if raw_location else DEFAULT_FOLDER_LOCATION, folder_name)

        try:
            os.makedirs(folder_path, exist_ok=True)
            return f"✅ Folder created at {folder_path}"
        except Exception as e:
            return f"❌ Failed to create folder: {e}"





    elif any(word in command for word in ["create file", "make file", "new file"]):
        match = re.search(r"(?:file)?\s*(\S+\.\w+)\s*(?:in|on)?\s*((?:[a-zA-Z]:)?(?:\s*drive)?(?:\\?[\w\s]+)*)?", command)
        if match:
            file_name = match.group(1)
            location_raw = match.group(2)

            if not location_raw or location_raw.strip() == "":
                location = DEFAULT_FOLDER_LOCATION
            else:
                location_raw = location_raw.lower().replace("drive", "").replace(" in ", "\\").replace(" on ", "\\").strip()
                location_raw = location_raw.replace(":", ":\\") if ":" in location_raw else location_raw
                location = normalize_path(location_raw)

            return create_file(os.path.join(location, file_name))


    elif any(word in command for word in ["delete file", "remove file"]):
        match = re.search(r"file\s*(\S+\.\w+)\s*(?:from)?\s*(desktop|documents|downloads|pictures|music|videos)?", command)
        if match:
            file_name = match.group(1)
            location = get_special_folder(match.group(2)) if match.group(2) else os.getcwd()
            return delete_file(os.path.join(location, file_name))

    elif any(word in command for word in ["delete folder", "remove folder"]):
        match = re.search(r"folder\s*(\w+)\s*(?:from)?\s*(desktop|documents|downloads|pictures|music|videos)?", command)
        if match:
            folder_name = match.group(1)
            location = get_special_folder(match.group(2)) if match.group(2) else os.getcwd()
            return delete_folder(os.path.join(location, folder_name))

    elif "shutdown" in command:
        speak("Are you sure you want to shut down the system? Say yes or no.")
        response = listen()
        if "yes" in response:
            return shutdown()
        elif "timeout" in response or "unknown" in response:
            return "❌ Shutdown canceled due to unclear or no response."
        else:
            return "❌ Shutdown canceled."

    elif "restart" in command:
        speak("Are you sure you want to restart the system? Say yes or no.")
        response = listen()
        if "yes" in response:
            return restart()
        elif "timeout" in response or "unknown" in response:
            return "❌ Restart canceled due to unclear or no response."
        else:
            return "❌ Restart canceled."



    elif "bluetooth" in command.lower():
        try:
            bluetooth()
            return "🔵 Bluetooth toggled (simulated click)."
        except Exception as e:
            return f"❌ Bluetooth toggle failed: {e}"
        
    elif "wifi" in command.lower() or "wi-fi" in command.lower():
        try:
            wifi()
            return "📡 WiFi toggled (simulated click)."
        except Exception as e:
            return f"❌ WiFi toggle failed: {e}"
        
    elif "brightness" in command:
        # Try to extract a number (e.g. "set brightness to 70%")
        match = re.search(r"(\d+)", command)
        if match:
            level = int(match.group(1))
            return set_brightness(level)
        elif "max" in command or "full" in command:
            return set_brightness(100)
        elif "min" in command or "zero" in command or "off" in command:
            return set_brightness(0)
        elif "increase" in command or "up" in command:
            return set_brightness(80)  # Arbitrary increase, you can improve this with state memory
        elif "decrease" in command or "down" in command:
            return set_brightness(30)  # Arbitrary decrease
        else:
            return "❌ Please specify brightness level from 0 to 100 or use words like 'increase', 'decrease', 'max'."

    elif "set volume" in command:
        # Try to extract a number (e.g. "set volume to 70%")
        match = re.search(r"(\d+)",command)
        if match:
            level = int(match.group(1))
            return set_volume(level)
        elif "max" in command or "full" in command:
            return set_volume(100)
        elif "min" in command or "zero" in command or "off" in command:
            return set_volume(0)
        elif "increase" in command or "up" in command:
            return set_volume(80)  # Arbitrary increase, you can improve this with state memory
        elif "decrease" in command or "down" in command:
            return set_volume(30)  # Arbitrary decrease
        else:
            return "❌ Please specify volume level from 0 to 100 or use words like 'increase', 'decrease', 'max'."


    elif "system info" in command or "laptop info" in command:
        return get_system_info()
    else:
        print(f"🔍 Unable to parse command: {command}")
        return "❌ Command not recognized or parsing failed. Please rephrase."



# ---------------------------
# Test Mode
# ---------------------------
if __name__ == "__main__":
    print("🧪 JARVIS Laptop Control - Test Mode")
    print("Type your command or 'exit' to quit.")
    while True:
        try:
            user_input = input("\n>>> ").strip()
            if user_input.lower() in ("exit", "quit"):
                print("👋 Exiting test mode.")
                break
            result = perform_laptop_command(user_input)
            print(result)
        except KeyboardInterrupt:
            print("\n👋 Exiting test mode.")
            break
