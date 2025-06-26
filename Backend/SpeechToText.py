# === Imports ===
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# === Global Variables & Override ===
_override_text = None  # Used to manually override speech input

def SetSpeechOverride(text):
    """Override speech input with predefined text."""
    global _override_text
    _override_text = text

# === Load Environment Variables ===
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  # Default input language is English

# === Create HTML File for Web-Based Speech Recognition ===
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{lang}';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''.replace('{lang}', InputLanguage)  # Inject language

# === Save HTML File ===
html_path = os.path.join("Data", "Voice.html")
os.makedirs("Data", exist_ok=True)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# === Selenium Driver Setup ===
current_dir = os.getcwd()
Link = f"file:///{current_dir.replace(os.sep, '/')}/Data/Voice.html"

chrome_options = Options()
chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')
chrome_options.add_argument("--use-fake-ui-for-media-stream")       # Auto grant mic permission
chrome_options.add_argument("--use-fake-device-for-media-stream")   # Prevent device errors
chrome_options.add_argument("--headless=new")                       # Run in background
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# === Assistant Status Handler (for GUI) ===
def SetAssistantStatus(Status):
    print(f"Assistant Status: {Status}")  # Replace with GUI update method

# === Query Modifier ===
def QueryModifier(Query):
    """Ensure queries are grammatically formatted as a question or statement."""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip(".?!") + "?"
    else:
        new_query = new_query.rstrip(".?!") + "."
    return new_query.capitalize()

# === Universal Translator ===
def UniversalTranslator(Text):
    """Translate any language to English."""
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# === Main Speech Recognition ===
def SpeechRecognition():
    global _override_text

    # Handle override if set
    if _override_text:
        text = _override_text
        _override_text = None
        if InputLanguage.lower().startswith("en"):
            return QueryModifier(text)
        else:
            SetAssistantStatus("Translating...")
            return QueryModifier(UniversalTranslator(text))

    # Launch local speech HTML interface
    driver.get(Link)
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # Get recognized text from browser
            Text = driver.find_element(by=By.ID, value="output").text.strip()

            if Text:
                driver.find_element(by=By.ID, value="end").click()
                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass  # Ignore occasional read failures

# === Test Entry Point ===
if __name__ == "__main__":
    print("Listening for speech input.")
    while True:
        recognized_text = SpeechRecognition()
        print(f"Recognized: {recognized_text}")
