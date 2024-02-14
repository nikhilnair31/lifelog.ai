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
config_file = 'config.txt'
model_combobox = None
default_openai_api_key = ''
default_downscale_perc = 25
default_system_prompt = "Explain this screenshot of the user's desktop in detail"
# endregion

# region Configuration
def load_config():
    global default_openai_api_key
    try:
        with open(config_file, 'r') as file:
            default_openai_api_key = file.read().strip()
    except FileNotFoundError:
        print("Config file not found. Using default OpenAI API key.")
    except Exception as e:
        print("Error loading config file:", e)

def save_config(api_key):
    try:
        with open(config_file, 'w') as file:
            file.write(api_key)
    except Exception as e:
        print("Error saving config file:", e)
# endregion

# region Image LLM Related
def send_image_to_api(image_bytes):
    """Determine which API to call based on the model selection and send the screenshot."""

    print(f'Sending Screenshot to API...')
    
    if model_combobox.get() == "GPT":
        response = call_open_ai_api(image_bytes)
    elif model_combobox.get() == "Moondream":
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
        original_image_bytes = take_screenshot()
        response = send_image_to_api(original_image_bytes)
        response_text = str(response)

        downscaled_image = downscale_image(original_image_bytes, quality=default_downscale_perc)
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
    save_config(new_openai_api_key)
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

    global root, db_path, default_system_prompt, model_combobox, compression_selection

    load_config()
    initialize_db(db_path) 
    
    # region Initial
    main_color_100 = '#ffffff'
    main_color_500 = '#878787'
    main_color_1000 = '#141414'
    accent_color_100 = '#ab36ff'
    width = 400
    height = 800

    root = tk.Tk()
    root.config(bg=main_color_100)
    root.title("EYES")

    # Calculate screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate x and y position for root window
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    title_label = tk.Label(root, text="EYES", bg=main_color_100, fg=main_color_1000, font=('Arial', 20, 'bold'))
    title_label.pack(pady=(10, 5))
    # endregion

    # region Config
    frame_config = tk.Frame(root, bg=main_color_100)
    frame_config.pack(pady=(10, 5))
    config_label = tk.Label(frame_config, text="Config", bg=main_color_100, fg=main_color_1000, font=('Arial', 16, 'bold'))
    config_label.pack(pady=(5, 10))
    # Interval
    label_interval = tk.Label(frame_config, text="Interval", bg=main_color_100, fg=main_color_1000)
    label_interval.pack()
    interval_entry = tk.Entry(frame_config, width=30)
    interval_entry.pack()
    interval_entry.insert(0, str(interval))
    interval_entry.bind('<FocusOut>', lambda event: update_interval(interval_entry.get()))
    # endregion

    # region Image Options
    frame_image = tk.Frame(root, bg=main_color_100)
    frame_image.pack(pady=(10, 5))
    image_options_label = tk.Label(frame_image, text="Image Options", bg=main_color_100, fg=main_color_1000, font=('Arial', 16, 'bold'))
    image_options_label.pack(pady=(10, 5))
    # API Image Quality
    label_api_image_quality = tk.Label(frame_image, text="API Image Quality", bg=main_color_100, fg=main_color_1000)
    label_api_image_quality.pack()
    image_quality_level_list = ["auto", "low", "high"]
    quality_combobox = ttk.Combobox(frame_image, values=image_quality_level_list, width=30)
    quality_combobox.set(image_quality_level_list[1])
    quality_combobox.pack()
    # Saved Image Compression
    label_saved_image_compression = tk.Label(frame_image, text="Saved Image Compression", bg=main_color_100, fg=main_color_1000)
    label_saved_image_compression.pack()
    compression_level_list = [5, 15, 25, 50, 75]
    compression_combobox = ttk.Combobox(frame_image, values=compression_level_list, width=30)
    compression_combobox.set(compression_level_list[2])
    compression_combobox.pack()
    # endregion

    # region Model Options
    frame_model = tk.Frame(root, bg=main_color_100)
    frame_model.pack(pady=(10, 5))
    model_options_label = tk.Label(frame_model, text="Model Options", bg=main_color_100, fg=main_color_1000, font=('Arial', 16, 'bold'))
    model_options_label.pack(pady=(10, 5))
    # API Key
    label_api_key = tk.Label(frame_model, text="API Key", bg=main_color_100, fg=main_color_1000)
    label_api_key.pack()
    openai_api_key_entry = tk.Entry(frame_model, width=30, show="*")
    openai_api_key_entry.pack()
    openai_api_key_entry.insert(0, str(default_openai_api_key))
    openai_api_key_entry.bind('<FocusOut>', lambda event: update_openai_api_key(openai_api_key_entry.get()))
    # Model
    label_model = tk.Label(frame_model, text="Model", bg=main_color_100, fg=main_color_1000)
    label_model.pack()
    model_list = ["GPT", "Moondream"]
    model_combobox = ttk.Combobox(frame_model, values=model_list, width=30)
    model_combobox.configure(background=main_color_100, foreground=main_color_1000)
    model_combobox.set(model_list[0])
    model_combobox.pack()
    # System Prompt
    label_system_prompt = tk.Label(frame_model, text="System Prompt", bg=main_color_100, fg=main_color_1000)
    label_system_prompt.pack()
    system_prompt_entry = tk.Text(frame_model, width=30, height=3)
    system_prompt_entry.pack()
    system_prompt_entry.insert(1.0, default_system_prompt)
    system_prompt_entry.bind('<FocusOut>', lambda event: update_system_prompt(system_prompt_entry.get()))
    # endregion
    
    # region Buttons
    frame_button = tk.Frame(root, bg=main_color_100)
    frame_button.pack(pady=(10, 5))
    start_button = tk.Button(
        frame_button, 
        text="Start",  
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, width=30, height=2,
        command=lambda: start_screenshot_process()
    )
    start_button.grid(row=0, column=0, padx=5, pady=10)
    stop_button = tk.Button(
        frame_button, 
        text="Stop", 
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, width=30, height=2,
        command=lambda: stop_screenshot_process()
    )
    stop_button.grid(row=1, column=0, padx=5, pady=10)
    # endregion
    # endregion
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
# endregion

if __name__ == "__main__":
    print(f'Starting EYES...\n')
    create_ui()