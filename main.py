import os
import base64
import tkinter as tk
from tkinter import ttk
from threading import Thread
import time
import sqlite3
import requests
from PIL import Image
from dotenv import load_dotenv
from screeninfo import get_monitors
from gradio_client import Client
from transformers import AutoModelForCausalLM, CodeGenTokenizerFast as Tokenizer
import io
import pyautogui

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

# Global variables to manage the screenshot loop
running = False
interval = 5000
db_path = 'data/screenshots.db'
model_selection = None
quality_selection = None
default_system_prompt = "What's in this image?"

def encode_image(image_bytes):
    """Encode image bytes to base64."""
    return base64.b64encode(image_bytes).decode('utf-8')

def send_image_to_api(image_bytes):
    """Determine which API to call based on the model selection and send the screenshot."""
    print(f'Sending Screenshot to API...')
    
    if model_selection.get() == "GPT-4V":
        response = call_open_ai_api(image_bytes)
    elif model_selection.get() == "Moondream":
        response = call_moondream_local(image_bytes)
    else:
        print("Invalid model selection.")
        return None
    
    return response
def call_open_ai_api(image_bytes):
    """Send the screenshot to the API and return the response."""

    print(f'Calling OpenAI API...')
    
    start_time = time.time()  # Capture start time

    base64_image = encode_image(image_bytes)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What's in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print(f'Received response in {elapsed_time:.2f} seconds.')  # Print the elapsed time to two decimal places
    
    return response.json()
def call_moondream_api(image_bytes):
    print(f'Calling Moondream API...')

    # Convert bytes image to a base64 string for URL
    base64_image = encode_image(image_bytes)
    # image_data_url = f"data:image/jpeg;base64,{base64_image}"

    # Initialize the Gradio client with your Moondream API URL
    client = Client("https://vikhyatk-moondream1.hf.space/--replicas/1hkz3/")

    # Make the prediction (API call)
    try:
        result = client.predict(
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png",   # This should be adjusted if your API expects a file path or a different format
            default_system_prompt,    # Adjust this as per the requirements of your API
            api_name="/answer_question"  # Update this endpoint as per your actual Moondream API endpoint
        )
        print("Moondream API Response:", result)
        return result
    except Exception as e:
        print("An error occurred while calling Moondream API:", str(e))
        return ""
def call_moondream_local(image_bytes):
    print(f'Calling Moondream Local...')

    model_id = "vikhyatk/moondream1"
    model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
    tokenizer = Tokenizer.from_pretrained(model_id)
    # enc_image = model.encode_image(image_bytes)

    # Make the prediction
    try:
        result = model.answer_question(image_bytes, "<QUESTION>", tokenizer)

        print("Moondream Local Response:", result)
        return result
    except Exception as e:
        print("An error occurred while calling Moondream Local:", str(e))
        return ""

def take_screenshot():
    print(f'Took Screenshot!')

    screenshot = pyautogui.screenshot()
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()
def take_screenshot_better():
    screenshots = []
    for m in get_monitors():
        print(f"Capturing screen: {m.name} at resolution {m.width}x{m.height}")
        screenshot = pyautogui.screenshot(region=(m.x, m.y, m.width, m.height))
        screenshots.append(screenshot)

    # Assuming we have at least two screenshots and we want to adjust the second one to match the first one's height
    if len(screenshots) >= 2:
        first_height = screenshots[0].size[1]
        second_screenshot = screenshots[1]
        second_width, second_height = second_screenshot.size
        # Calculate the new width for the second screenshot to maintain its aspect ratio
        new_second_width = int(first_height * (second_width / second_height))
        resized_second_screenshot = second_screenshot.resize((new_second_width, first_height), Image.Resampling.LANCZOS)
        
        # Create a new blank image with a width that is the sum of both screenshots' widths and a height matching the first screenshot
        total_width = screenshots[0].size[0] + new_second_width
        stitched_image = Image.new('RGB', (total_width, first_height))
        
        # Paste the first screenshot and the resized second screenshot into the stitched image
        stitched_image.paste(screenshots[0], (0, 0))
        stitched_image.paste(resized_second_screenshot, (screenshots[0].size[0], 0))
        
        # Save or process the stitched image
        img_byte_arr = io.BytesIO()
        stitched_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    else:
        # Fallback or other handling if there's only one screenshot
        img_byte_arr = io.BytesIO()
        screenshots[0].save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

def downscale_image(image):
    basewidth = 320
    img = Image.open(io.BytesIO(image))
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
def downscale_image_better(image_bytes, quality=90):
    """
    Downscale the image to a specified width and adjust quality.
    
    Parameters:
    - image_bytes: Image data in bytes.
    - quality: Desired quality percentage (1-100).
    
    Returns:
    - Bytes of the downscaled and quality-adjusted image.
    """

    print(f'Downscaling Screenshot...')
    
    img = Image.open(io.BytesIO(image_bytes))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=quality)
    
    return img_byte_arr.getvalue()

def initialize_db(db_file):
    print(f'Initializing DB...')

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS screenshots
                 (timestamp TEXT, image BLOB, api_response TEXT)''')
    conn.commit()
    conn.close()

    print(f'Initialized\n')

def save_to_db(timestamp, image, response):
    print(f'Saving to DB...')

    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO screenshots VALUES (?, ?, ?)", (timestamp, image, response))
    conn.commit()
    conn.close()

    print(f'Saved!\n')

def screenshot_loop():
    global running, interval

    while running:
        image_bytes = take_screenshot_better()
        
        # Convert the quality selection to an appropriate JPEG quality integer.
        quality_factor = str(quality_selection.get())
        if quality_factor == '75%':
            jpeg_quality = 75
        elif quality_factor == '50%':
            jpeg_quality = 50
        elif quality_factor == '25%':
            jpeg_quality = 25
        else:
            jpeg_quality = 50

        downscaled_image = downscale_image_better(image_bytes, quality=jpeg_quality)
        response = send_image_to_api(downscaled_image)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        # Convert response to a string or extract the needed info from it before saving
        response_text = str(response)
        save_to_db(timestamp, downscaled_image, response_text)
        time.sleep(interval)

def start_screenshot_process():
    print(f'Started Screenshot Process')
    global running
    running = True
    thread = Thread(target=screenshot_loop)
    thread.start()

def stop_screenshot_process():
    print(f'Stopped Screenshot Process')
    global running
    running = False

def update_interval(new_interval):
    print(f'Updating Interval')
    global interval
    interval = int(new_interval)
def update_system_prompt(new_system_prompt):
    print(f'Updating Default System Prompt')
    global default_system_prompt
    default_system_prompt = str(new_system_prompt)

def on_closing():
    print("Closing application...")
    global running
    if running:
        stop_screenshot_process()
    root.destroy()

def create_ui():
    print(f'Building UI...\n')

    global db_path, root, default_system_prompt, model_selection, quality_selection

    initialize_db(db_path) 

    root = tk.Tk()
    root.title("EYES")

    # Set default window size
    root.geometry('600x400')  # Width x Height

    # Inputs
    tk.Label(root, text="Interval (seconds)").pack()
    interval_entry = tk.Entry(root)
    interval_entry.pack()
    interval_entry.insert(0, str(interval))

    tk.Label(root, text="System Prompt").pack()
    system_prompt_entry = tk.Entry(root)
    system_prompt_entry.pack()
    system_prompt_entry.insert(0, default_system_prompt)
    
    # Dropdowns
    tk.Label(root, text="Select Quality:").pack()
    quality_selection = ttk.Combobox(root, values=["75%", "50%", "25%"])
    quality_selection.pack()
    quality_selection.set("25%")
    
    tk.Label(root, text="Select Model:").pack()
    model_selection = ttk.Combobox(root, values=["GPT-4V", "Moondream"])
    model_selection.pack()
    model_selection.set("GPT-4V")

    # Buttons
    tk.Button(root, text="Start", command=lambda: start_screenshot_process()).pack()
    tk.Button(root, text="Stop", command=lambda: stop_screenshot_process()).pack()
    tk.Button(root, text="Update System Prompt", command=lambda: update_system_prompt(system_prompt_entry.get())).pack()
    tk.Button(root, text="Update Interval", command=lambda: update_interval(interval_entry.get())).pack()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    print(f'Starting EYES...\n')

    create_ui()
