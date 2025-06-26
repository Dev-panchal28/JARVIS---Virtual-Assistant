# === Imports ===
import pygame
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# === Load Environment Variables ===
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Voice name for the assistant

# === Generate TTS Audio File ===
async def TextToAudioFile(text: str, file_path: str) -> None:
    """Create a speech MP3 from text using edge-tts."""
    if os.path.exists(file_path):
        os.remove(file_path)
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

# === Play Audio with Optional Interrupt Support ===
def TTS(text: str, interrupt_check=lambda: True):
    """Play TTS audio, support interruption via a callback."""
    file_path = "Data/speech.mp3"

    try:
        asyncio.run(TextToAudioFile(text, file_path))  # Generate audio file

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            if not interrupt_check():  # Stop playback if interrupted
                pygame.mixer.music.stop()
                break
            clock.tick(10)

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Cleanup error: {e}")

# === Smart Chunked Text-to-Speech Handler ===
def TextToSpeech(text: str, interrupt_check=lambda: True):
    """Split long text into chunks and speak each one with interruption support."""
    max_length = 300  # Max characters per chunk
    chunks = []

    remaining_text = text.strip()
    while len(remaining_text) > max_length:
        split_idx = remaining_text.rfind('.', 0, max_length)
        if split_idx == -1:
            split_idx = max_length
        chunk = remaining_text[:split_idx + 1].strip()
        chunks.append(chunk)
        remaining_text = remaining_text[split_idx + 1:].strip()

    if remaining_text:
        chunks.append(remaining_text)

    for chunk in chunks:
        if not interrupt_check():  # Allow speech to stop on user signal
            break
        TTS(chunk, interrupt_check)

# === Test Entry Point ===
if __name__ == "__main__":
    while True:
        text = input("Enter the text: ")
        TextToSpeech(text)
