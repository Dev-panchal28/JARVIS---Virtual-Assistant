import pygame
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# Async function to generate TTS audio file
async def TextToAudioFile(text: str, file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

# Function to play the audio and support interruption
def TTS(text: str, interrupt_check=lambda: True):
    file_path = "Data/speech.mp3"

    try:
        asyncio.run(TextToAudioFile(text, file_path))

        if not pygame.mixer.get_init():  # ✅ Check before init
            pygame.mixer.init()

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            if not interrupt_check():
                pygame.mixer.music.stop()
                break
            clock.tick(10)

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            if pygame.mixer.get_init():  # ✅ Check before cleanup
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Cleanup error: {e}")


# Main entry point to handle long text smartly with chunking
def TextToSpeech(text: str, interrupt_check=lambda: True):
    max_length = 300  # maximum characters per chunk
    chunks = []

    remaining_text = text.strip()
    while len(remaining_text) > max_length:
        split_idx = remaining_text.rfind('.', 0, max_length)
        if split_idx == -1:
            split_idx = max_length
        # Include the period in the chunk if found
        chunk = remaining_text[:split_idx + 1].strip()
        chunks.append(chunk)
        remaining_text = remaining_text[split_idx + 1:].strip()

    if remaining_text:
        chunks.append(remaining_text)

    for chunk in chunks:
        if not interrupt_check():
            break
        TTS(chunk, interrupt_check)

# Test independently
if __name__ == "__main__":
    while True:
        text = input("Enter the text: ")
        TextToSpeech(text)