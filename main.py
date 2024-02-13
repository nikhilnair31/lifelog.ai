# region Packages
import os
import io
import time
import base64
import sqlite3
import tempfile
import requests
import pyautogui
from mss import mss
import tkinter as tk
from PIL import Image
from tkinter import ttk
from threading import Thread
from dotenv import load_dotenv
from gradio_client import Client
from screeninfo import get_monitors
# endregion

# region Setup
# Env Vars
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Global variables
running = False
interval = 2
db_path = 'data/screenshots.db'
model_selection = None
quality_selection = None
default_system_prompt = "What's in this image?"
# endregion

# region Image LLM Related
def send_image_to_api(image_bytes):
    """Determine which API to call based on the model selection and send the screenshot."""

    print(f'Sending Screenshot to API...')
    
    if model_selection.get() == "GPT":
        response = call_open_ai_api(image_bytes)
    elif model_selection.get() == "Moondream":
        response = call_moondream_api(image_bytes)
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

    # Load the image from bytes for a sanity check or manipulation if needed
    img = Image.open(io.BytesIO(image_bytes))

    # Save the image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg') as tmpfile:
        img.save(tmpfile, format="JPEG")
        tmpfile_path = tmpfile.name

    # Initialize the Gradio client with your Moondream API URL
    client = Client("https://vikhyatk-moondream1.hf.space/--replicas/1hkz3/")

    # Make the prediction (API call)
    try:
        result = client.predict(
            tmpfile_path,
            default_system_prompt,  
            api_name="/answer_question"
        )
        print("Moondream API Response:", result)
        return result
    except Exception as e:
        print("An error occurred while calling Moondream API:", str(e))
        return ""
    finally:
        # Optionally delete the temp file if not needed anymore
        os.unlink(tmpfile_path)
def encode_image(image_bytes):
    """Encode image bytes to base64."""
    return base64.b64encode(image_bytes).decode('utf-8')
# endregion

# region Image Related
def take_screenshot():
    screenshots = []
    with mss() as sct:
        for monitor_number, monitor in enumerate(sct.monitors[1:], start=1):  # Skip the first entry which is the entire screen
            print(f"Capturing screen: Monitor {monitor_number} at resolution {monitor['width']}x{monitor['height']}")
            sct_img = sct.grab(monitor)
            screenshot = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
            screenshots.append(screenshot)

    if len(screenshots) >= 2:
        first_screenshot = screenshots[0]
        first_width, first_height = first_screenshot.size

        second_screenshot = screenshots[1]
        resized_second_screenshot = second_screenshot.resize((first_width, first_height), Image.Resampling.LANCZOS)

        stitched_image = Image.new('RGB', (first_width * 2, first_height))
        stitched_image.paste(first_screenshot, (0, 0))
        stitched_image.paste(resized_second_screenshot, (first_width, 0))

        img_byte_arr = io.BytesIO()
        stitched_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    else:
        img_byte_arr = io.BytesIO()
        screenshots[0].save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

def downscale_image(image_bytes, quality=90):
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
# endregion

# region DB Related
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
# endregion

# region Primary Loop Related
def screenshot_loop():
    print(f'Started Screenshot Loop...')

    global running, interval

    while running:        
        print(f'Running')

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

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        image_bytes = take_screenshot()
        downscaled_image = downscale_image(image_bytes, quality=jpeg_quality)
        response = send_image_to_api(downscaled_image)
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
# endregion

# region UI Related
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

    global root, db_path, default_system_prompt, model_selection, quality_selection

    initialize_db(db_path) 
    
    # Define modern color scheme
    background_color = '#ffffff'
    accent_color = '#ccb3ff'
    width = 350
    height = 650

    root = tk.Tk()
    root.config(bg=background_color)
    root.title("EYES")
    root.geometry(f'{width}x{height}')
    # root.minsize(width, height)
    # root.maxsize(width, height)

    # Inputs
    interval_label = tk.Label(root, text="Interval (seconds)")
    interval_label.pack(pady=(10, 5))
    interval_entry = tk.Entry(root)
    interval_entry.pack(pady=5)
    interval_entry.insert(0, str(interval))

    tk.Label(root, text="System Prompt").pack()
    system_prompt_entry = tk.Entry(root)
    system_prompt_entry.pack()
    system_prompt_entry.insert(0, default_system_prompt)
    
    # Dropdowns
    quality_label = tk.Label(root, text="Select Quality:", bg=background_color)
    quality_label.pack(pady=(10, 5))
    quality_list = ["25%", "50%", "75%"]
    quality_selection = ttk.Combobox(
        root, 
        values=quality_list
    )
    quality_selection.configure(background='lightgray', foreground='blue')
    quality_selection.pack(pady=10, padx=5)
    quality_selection.set(quality_list[0])
    
    model_label = tk.Label(root, text="Select Model:", bg=background_color)
    model_label.pack(pady=(10, 5))
    model_list = ["GPT", "Moondream"]
    model_selection = ttk.Combobox(
        root, 
        values=model_list
    )
    model_selection.configure(background='lightgray', foreground='blue')
    model_selection.pack(pady=10, padx=5)
    model_selection.set(model_list[0])

    # Buttons
    start_button = tk.Button(
        root, 
        text="Start",  
        bg=accent_color, fg='white', borderwidth=0, highlightthickness=0, width=20, height=2,
        command=lambda: start_screenshot_process()
    ).pack(pady=10, padx=5, ipadx=10)
    
    stop_button = tk.Button(
        root, 
        text="Stop", 
        bg=accent_color, fg='white', borderwidth=0, highlightthickness=0, width=20, height=2,
        command=lambda: stop_screenshot_process()
    ).pack(pady=10, padx=5, ipadx=10)
    
    update_system_prompt_button = tk.Button(
        root, 
        text="Update System Prompt", 
        bg=accent_color, fg='white', borderwidth=0, highlightthickness=0, width=20, height=2,
        command=lambda: update_system_prompt(system_prompt_entry.get())
    ).pack(pady=10, padx=5, ipadx=10)
    
    update_interval_button = tk.Button(
        root, 
        text="Update Interval", 
        bg=accent_color, fg='white', borderwidth=0, highlightthickness=0, width=20, height=2,
        command=lambda: update_interval(interval_entry.get())
    ).pack(pady=10, padx=5, ipadx=10)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
# endregion

if __name__ == "__main__":
    print(f'Starting EYES...\n')
    create_ui()