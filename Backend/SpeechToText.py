from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# --- Global override mechanism ---
_override_text = None

def SetSpeechOverride(text):
    global _override_text
    _override_text = text

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

# Prepare the HTML file for speech recognition with dynamic language
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
</html>'''

# Replace placeholder with actual language
HtmlCode = HtmlCode.replace('{lang}', InputLanguage)

# Save the HTML to Data folder
html_path = os.path.join("Data", "Voice.html")
os.makedirs("Data", exist_ok=True)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Build the full path for selenium
current_dir = os.getcwd()
Link = f"file:///{current_dir.replace(os.sep, '/')}/Data/Voice.html"

# Setup Selenium WebDriver
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # Remove this line to debug in visible browser

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def SetAssistantStatus(Status):
    # Dummy function - replace this with the one from your actual GUI
    print(f"Assistant Status: {Status}")

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    global _override_text

    if _override_text:
        text = _override_text
        _override_text = None
        if InputLanguage.lower().startswith("en"):
            return QueryModifier(text)
        else:
            SetAssistantStatus("Translating...")
            return QueryModifier(UniversalTranslator(text))

    driver.get(Link)
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text.strip()

            if Text:
                driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass

if __name__ == "__main__":
    print("Listening for speech input.")
    while True:
        recognized_text = SpeechRecognition()
        print(f"Recognized: {recognized_text}")
