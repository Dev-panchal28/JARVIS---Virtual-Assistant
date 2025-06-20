import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# --- Setup & Configuration ---
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
DATA_FOLDER = "Data"
INPUT_FILE = os.path.join("Frontend", "Files", "ImageGeneration.data")

# Get API key securely
api_key = get_key('.env', 'HuggingFaceAPIKey')
if not api_key:
    raise EnvironmentError("HuggingFaceAPIKey not found in .env file.")
headers = {"Authorization": f"Bearer {api_key}"}


# --- Helper: Show generated images ---
def open_images(prompt):
    prompt_sanitized = prompt.replace(" ", "_")
    for i in range(1, 5):
        image_filename = f"{prompt_sanitized}{i}.jpg"
        image_path = os.path.join(DATA_FOLDER, image_filename)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Delay to allow each image to open
        except IOError:
            print(f"Unable to open {image_path}")


# --- Async: Call Hugging Face API ---
async def query(payload):
    try:
        response = await asyncio.to_thread(
            requests.post,
            API_URL,
            headers=headers,
            json=payload,
            timeout=60  # Add timeout
        )
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Image generation request failed: {e}")
        return None



# --- Async: Generate multiple images ---
async def generate_images(prompt: str):
    prompt_sanitized = prompt.replace(" ", "_")
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, ultra detailed, 8k, sharp focus, high realism, cinematic lighting, trending on ArtStation"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    os.makedirs(DATA_FOLDER, exist_ok=True)
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(DATA_FOLDER, f"{prompt_sanitized}{i + 1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
        else:
            print(f"Image {i + 1} generation failed.")


# --- Sync Wrapper: Generate and Open ---
def generate_and_open_images(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)


# --- File Monitoring Loop ---
def monitor_file():
    #print("Monitoring for image generation requests...")

    while True:
        try:
            with open(INPUT_FILE, "r") as f:
                data = f.read().strip()

            if not data:
                sleep(1)
                continue

            Prompt, Status = data.split(",")

            if Status.strip() == "True":
                print("Generating images...")
                generate_and_open_images(prompt=Prompt.strip())

                with open(INPUT_FILE, "w") as f:
                    f.write("False,False")

                print("Image generation completed.")
                break

            else:
                sleep(1)

        except FileNotFoundError:
            print(f"File not found: {INPUT_FILE}")
            sleep(1)
        except ValueError:
            print(f"Malformed data in {INPUT_FILE}. Expected format: 'prompt,True'")
            sleep(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sleep(1)


# --- Run ---
if __name__ == "__main__":
    monitor_file()
