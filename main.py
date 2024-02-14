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
from gradio_client import Client
from screeninfo import get_monitors
# endregion

# region Setup
# Global variables
running = False
interval = 5
db_path = 'data/screenshots.db'
model_selection = None
default_openai_api_key = ''
default_downscale_perc = 25
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
        "Authorization": f"Bearer {default_openai_api_key}"
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

    global running, interval, default_downscale_perc

    while running:        
        print(f'Running')

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        image_bytes = take_screenshot()
        downscaled_image = downscale_image(image_bytes, quality=default_downscale_perc)
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
def update_openai_api_key(new_openai_api_key):
    print(f'Updating OpenAI API Key')
    global default_openai_api_key
    default_openai_api_key = str(new_openai_api_key)
def update_downscale_level(new_downscale_perc):
    print(f'Updating Downscale %')
    global default_downscale_perc
    default_downscale_perc = int(new_downscale_perc)

def on_closing():
    print("Closing application...")
    global running
    if running:
        stop_screenshot_process()
    root.destroy()

def create_ui():
    print(f'Building UI...\n')

    global root, db_path, default_system_prompt, model_selection, compression_selection

    initialize_db(db_path) 
    
    # Define modern color scheme
    main_color_100 = '#141414'
    main_color_500 = '#878787'
    main_color_1000 = '#e6e6e6'
    accent_color_100 = '#ab36ff'
    width = 350
    height = 650

    root = tk.Tk()
    root.config(bg=main_color_100)
    root.title("EYES")
    root.geometry(f'{width}x{height}')
    # root.minsize(width, height)
    # root.maxsize(width, height)

    # Inputs
    openai_api_key_label = tk.Label(
        root, 
        text="Enter OpenAI API Key",
        bg=main_color_100,
        fg=main_color_1000
    )
    openai_api_key_label.pack(pady=(10, 5))
    openai_api_key_entry = tk.Entry(
        root, 
        width=20,
        show="*",
    )
    openai_api_key_entry.pack(pady=5)
    openai_api_key_entry.insert(0, str(default_openai_api_key))
    openai_api_key_entry.bind('<FocusOut>', lambda event: update_openai_api_key(openai_api_key_entry.get()))

    interval_label = tk.Label(
        root, 
        text="Interval (seconds)",
        bg=main_color_100,
        fg=main_color_1000
    )
    interval_label.pack(pady=(10, 5))
    interval_entry = tk.Entry(
        root, 
        width=20,
    )
    interval_entry.pack(pady=5)
    interval_entry.insert(0, str(interval))
    interval_entry.bind('<FocusOut>', lambda event: update_interval(interval_entry.get()))

    system_prompt_label = tk.Label(
        root, 
        text="System Prompt",
        bg=main_color_100,
        fg=main_color_1000
    )
    system_prompt_label.pack(pady=(10, 5))
    system_prompt_entry = tk.Entry(
        root, 
        width=20,
    )
    system_prompt_entry.pack()
    system_prompt_entry.insert(0, default_system_prompt)
    system_prompt_entry.bind('<FocusOut>', lambda event: update_system_prompt(system_prompt_entry.get()))

    # Dropdowns
    image_quality_label = tk.Label(
        root, 
        text="Select Quality:", 
        bg=main_color_100,
        fg=main_color_1000
    )
    image_quality_label.pack(pady=(10, 5))
    image_quality_level_list = ["auto", "low", "high"]
    image_quality_selection = ttk.Combobox(
        root, 
        values=image_quality_level_list, 
        width=20
    )
    image_quality_selection.configure(background='lightgray', foreground='blue')
    image_quality_selection.pack(pady=10, padx=5)
    image_quality_selection.set(image_quality_level_list[1])

    compression_label = tk.Label(
        root, 
        text="Select Quality %:", 
        bg=main_color_100,
        fg=main_color_1000
    )
    compression_label.pack(pady=(10, 5))
    compression_level_list = [25, 50, 75]
    compression_selection = ttk.Combobox(
        root, 
        values=compression_level_list, 
        width=20
    )
    compression_selection.configure(background='lightgray', foreground='blue')
    compression_selection.pack(pady=10, padx=5)
    compression_selection.set(compression_level_list[0])
    
    model_label = tk.Label(
        root, 
        text="Select Model:", 
        bg=main_color_100,
        fg=main_color_1000
    )
    model_label.pack(pady=(10, 5))
    model_list = ["GPT", "Moondream"]
    model_selection = ttk.Combobox(
        root, 
        values=model_list,
        width=20
    )
    model_selection.configure(background='lightgray', foreground='blue')
    model_selection.pack(pady=10, padx=5)
    model_selection.set(model_list[0])

    # Buttons
    start_button = tk.Button(
        root, 
        text="Start",  
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, width=20, height=2,
        command=lambda: start_screenshot_process()
    )
    start_button.pack(pady=10, padx=5)
    
    stop_button = tk.Button(
        root, 
        text="Stop", 
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, width=20, height=2,
        command=lambda: stop_screenshot_process()
    )
    start_button.pack(pady=10, padx=5)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
# endregion

if __name__ == "__main__":
    print(f'Starting EYES...\n')
    create_ui()