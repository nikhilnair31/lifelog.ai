# region Packages
import os
import io
import cv2
import json
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
from queue import Queue
from threading import Thread
from gradio_client import Client
from screeninfo import get_monitors
# endregion

# region Setup
# Global variables
global running, cap, photos_folder_path, screenshots_folder_path, sql_folder_path, db_path, config_file, default_text_model, default_image_model, default_interval, default_openai_api_key, default_together_api_key, default_downscale_perc, default_quality_val, default_system_prompt

NUM_THREADS = 2
running = False

photos_folder_path = 'data/photos/'
screenshots_folder_path = 'data/screenshots/'
sql_folder_path = 'data/sql/'

db_path = 'data/sql/data.db'
config_file = 'config.json'

default_text_model = 'GPT-3.5-Turbo'
default_image_model = 'GPT'
default_interval = 5
default_openai_api_key = ''
default_together_api_key = ''
default_downscale_perc = 25
default_quality_val = 'low'
default_system_prompt = "What do you see? Be precise. You have the screenshots of my screen! Tell what you see on the screen and text you see in details! It can be rick and morty series, terminal, twitter, vs code, and other! answer with cool details! Answer in 20 words max! Make a story about my screenshot day out of it! If you can't see make best guess!"

cap = None
# endregion

# region Configuration
def load_config():
    global config_file, default_text_model, default_image_model, default_interval, default_openai_api_key, default_together_api_key, default_downscale_perc, default_quality_val, default_system_prompt
    try:
        with open(config_file, 'r') as file:
            config_data = json.load(file)
            print(f"Config file : {config_data}\n")
            default_text_model = config_data.get('default_text_model', default_text_model)
            default_image_model = config_data.get('default_image_model', default_image_model)
            default_interval = config_data.get('default_interval', default_interval)
            default_openai_api_key = config_data.get('default_openai_api_key', default_openai_api_key)
            default_together_api_key = config_data.get('default_together_api_key', default_together_api_key)
            default_downscale_perc = config_data.get('default_downscale_perc', default_downscale_perc)
            default_quality_val = config_data.get('default_quality_val', default_quality_val)
            default_system_prompt = config_data.get('default_system_prompt', default_system_prompt)
    except FileNotFoundError:
        print("Config file not found. Creating empty and using defaults.")
        with open(config_file, 'w') as file:
            json.dump({
                'default_text_model': default_text_model,
                'default_image_model': default_image_model,
                'default_interval': default_interval,
                'default_openai_api_key': default_openai_api_key,
                'default_together_api_key': default_together_api_key,
                'default_downscale_perc': default_downscale_perc,
                'default_quality_val': default_quality_val,
                'default_system_prompt': default_system_prompt
            }, file)
            pass
    except Exception as e:
        print("Error loading config file:", e)

def save_config(key, new_val):
    try:
        with open(config_file, 'r') as file:
            config_data = json.load(file)
        config_data[key] = new_val
        with open(config_file, 'w') as outfile:
            json.dump(config_data, outfile)
    except Exception as e:
        print("Error saving config file:", e)
# endregion

# region DB Related
def initialize_db():
    print(f'Initializing DB...')

    global db_path, sql_folder_path
    
    if not os.path.exists(sql_folder_path):
        os.makedirs(sql_folder_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS screenshots
                 (timestamp TEXT, image BLOB, image_path TEXT, api_response TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS photos
                 (timestamp TEXT, image BLOB, image_path TEXT, api_response TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS summary
                 (timestamp TEXT, content TEXT)''')
    conn.commit()
    conn.close()

    print(f'Initialized!\n')

def save_to_screenshot_db(timestamp, image_bytes, image_path, response_text, content):
    print(f'Saving to Screenshots DB...')

    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO screenshots VALUES (?, ?, ?, ?, ?)", (timestamp, image_bytes, image_path, response_text, content))
    conn.commit()
    conn.close()

    print(f'Saved!\n')

def save_to_photo_db(timestamp, image_bytes, image_path, response, content):
    print(f'Saving to Photos DB...')

    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO photos VALUES (?, ?, ?, ?, ?)", (timestamp, image_bytes, image_path, response, content))
    conn.commit()
    conn.close()

    print(f'Saved!\n')

def save_to_summary_db(timestamp, content):
    print(f'Saving to Summary DB...')

    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO summary VALUES (?, ?)", (timestamp, content))
    conn.commit()
    conn.close()

    print(f'Saved!\n')

def retrieve_image_paths_from_db(table_name):
    print(f'Retrieving image paths from {table_name}...')

    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT image_path FROM {table_name} WHERE api_response IS NULL OR api_response = '' OR LENGTH(api_response)=0")
    rows = c.fetchall()
    conn.close()

    print(f'Retrieved!\n')

    return [row[0] for row in rows]

def retrieve_contents_from_db(table_name):
    print(f'Retrieving contents from {table_name}...')

    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"SELECT content FROM {table_name} WHERE content IS NOT NULL OR content != '' OR LENGTH(content)>0")
    rows = c.fetchall()
    conn.close()

    print(f'Retrieved!\n')

    return [row[0] for row in rows]

def update_api_response(table_name, filepath, response, content):
    print(f'Updating {table_name}...')

    global db_path

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"UPDATE {table_name} SET api_response = ? WHERE image_path = ?", (response, filepath))
    c.execute(f"UPDATE {table_name} SET content = ? WHERE image_path = ?", (content, filepath))
    conn.commit()
    conn.close()

    print(f'Updated!\n')
# endregion

# region Foundation Model Related
def send_image_to_api(image_bytes):
    """Determine which API to call based on the model selection and send the screenshot."""

    print(f'Sending Images to API...')
    
    if default_image_model == "GPT":
        response = call_gpt4v_api(image_bytes)
    elif default_image_model == "Moondream":
        response = call_moondream_api(image_bytes)
    else:
        print(f"Invalid model selection: {default_image_model}")
        return None
    
    return response
def call_gpt4v_api(image_bytes):
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
                        "text": default_system_prompt
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

def send_text_to_api(text_list):
    """Determine which API to call based on the model selection and send the screenshot."""

    print(f'Sending Text to API...')
    
    if default_text_model == "GPT-3.5-Turbo":
        response = call_together_api('gpt-3.5-turbo', "gpt", text_list)
    elif default_text_model == "GPT-4-Turbo":
        response = call_together_api('gpt-4-turbo-preview', "gpt", text_list)
    elif default_text_model == "Mixtral-8x7B-Instruct-v0.1":
        response = call_together_api('mistralai/Mixtral-8x7B-Instruct-v0.1', "together", text_list)
    elif default_text_model == "OpenHermes-Mistral-7B":
        response = call_together_api('teknium/OpenHermes-2p5-Mistral-7B', "together", text_list)
    else:
        print(f"Invalid model selection: {default_text_model}")
        return None
    
    return response
    """Send the contents to the API and return the response."""

    print(f'Calling GPT API...')
    
    start_time = time.time()  # Capture start time

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {default_openai_api_key}"
    }
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. You have received the description of screenshots and webcam images from the user. You need to summarize the day."
            },
            {
                "role": "user",
                "content": "Summarize today's events. Format it nicely in bullet poitns in HTML. Your WHOLE answer must be in HTML."
            },
            {
                "role": "assistant",
                "content": "\n".join(contents)
            }
        ]
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print(f'Received response in {elapsed_time:.2f} seconds.')  # Print the elapsed time to two decimal places
    
    return response.json()
def call_together_api(model_name, source, contents):
    """Send the contents to the API and return the response."""

    print(f'Calling Together API...')
    
    start_time = time.time()
    
    if source == "gpt":
        url = "https://api.openai.com/v1/chat/completions"
        api_key = default_openai_api_key
    else:
        url = "https://api.together.xyz/v1/chat/completions"
        api_key = default_together_api_key

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. You have received the description of screenshots and webcam images from the user. You need to summarize the day."
            },
            {
                "role": "user",
                "content": "Summarize today's events. Format it nicely in bullet poitns in HTML. Your WHOLE answer must be in HTML."
            },
            {
                "role": "assistant",
                "content": "\n".join(contents)
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print(f'Received response in {elapsed_time:.2f} seconds.')  # Print the elapsed time to two decimal places
    
    return response.json()

def encode_image(image_bytes):
    """Encode image bytes to base64."""
    return base64.b64encode(image_bytes).decode('utf-8')
# endregion

# region Image Related
def take_screenshot():
    with mss() as sct:
        # The first entry of sct.monitors is the entire screen
        monitor = sct.monitors[0]
        # Determine the width and height for cropping
        width = min(3840, monitor['width'])
        height = min(1080, monitor['height'])

        # Grab the image
        sct_img = sct.grab({
            "top": monitor["top"], 
            "left": monitor["left"], 
            "width": width, 
            "height": height
        })
        
        screenshot = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)

    # Save the image to a byte array
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def take_photo():
    global cap

    ret, frame = cap.read()

    # Convert the frame to JPEG format
    _, img_encoded = cv2.imencode('.jpeg', frame)

    # Convert the encoded image array to bytes
    img_byte_arr = img_encoded.tobytes()

    return img_byte_arr

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

# region Primary Loop Related
def screenshot_loop():
    print(f'Started Screenshot Loop...')

    global running, screenshots_folder_path, default_interval, default_downscale_perc
    
    if not os.path.exists(screenshots_folder_path):
        os.makedirs(screenshots_folder_path)

    while running:        
        print(f'Running Screenshot Loop')

        # Pull data
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        filename = time.strftime('%Y-%m-%d-%H-%M-%S')
        original_image_bytes = take_screenshot()
        
        # Save the original image to the specified path
        image_filename = f"{filename}.jpeg"
        image_path = os.path.join(screenshots_folder_path, image_filename)
        with open(image_path, 'wb') as f:
            f.write(original_image_bytes)

        # Save data to SQL
        downscaled_image_bytes = downscale_image(original_image_bytes, quality=default_downscale_perc)
        save_to_screenshot_db(timestamp, downscaled_image_bytes, image_filename, '', '')

        if not running:
            break
        time.sleep(default_interval)

def photo_loop():
    print(f'Started Photo Loop...')

    global running, photos_folder_path, default_interval, default_downscale_perc

    if not os.path.exists(photos_folder_path):
        os.makedirs(photos_folder_path)

    while running:        
        print(f'Running Photo Loop')

        # Pull data
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        filename = time.strftime('%Y-%m-%d-%H-%M-%S')
        original_image_bytes = take_photo()
        
        # Save the original image to the specified path
        image_filename = f"{filename}.jpeg"
        image_path = os.path.join(photos_folder_path, image_filename)
        with open(image_path, 'wb') as f:
            f.write(original_image_bytes)

        downscaled_image_bytes = downscale_image(original_image_bytes, quality=default_downscale_perc)
        save_to_photo_db(timestamp, downscaled_image_bytes, image_filename, '', '')

        if not running:
            break
        time.sleep(default_interval)

# FIXME: Simplify async/thread logic
def api_loop():
    global NUM_THREADS, photos_folder_path, screenshots_folder_path

    screenshots_filepaths = retrieve_image_paths_from_db('screenshots')
    photos_filepaths = retrieve_image_paths_from_db('photos')
    # print(f'screenshots_filepaths: {len(screenshots_filepaths)}\nphotos_filepaths: {len(photos_filepaths)}')
    
    # Create a queue for screenshots and start worker threads
    screenshots_queue = Queue()
    for filepath in screenshots_filepaths:
        screenshots_queue.put(filepath)
    screenshots_threads = []
    for _ in range(NUM_THREADS):
        thread = Thread(target=worker, args=(screenshots_queue, screenshots_folder_path, 'screenshots'))
        thread.start()
        screenshots_threads.append(thread)

    # Create a queue for photos and start worker threads
    photos_queue = Queue()
    for filepath in photos_filepaths:
        photos_queue.put(filepath)
    photos_threads = []
    for _ in range(NUM_THREADS):
        thread = Thread(target=worker, args=(photos_queue, photos_folder_path, 'photos'))
        thread.start()
        photos_threads.append(thread)

    # Wait for all threads to finish
    screenshots_queue.join()
    for _ in range(NUM_THREADS):
        screenshots_queue.put(None)
    for thread in screenshots_threads:
        thread.join()

    photos_queue.join()
    for _ in range(NUM_THREADS):
        photos_queue.put(None)
    for thread in photos_threads:
        thread.join()
def worker(file_queue, folder_path, table_name):
    while True:
        filepath = file_queue.get()
        if filepath is None:
            break
        image_path = os.path.join(folder_path, filepath)
        with open(image_path, 'rb') as file:
            image_bytes = file.read()
        response = send_image_to_api(image_bytes)
        response_text = str(response)
        content_text = response['choices'][0]['message']['content']
        update_api_response(table_name, filepath, response_text, content_text)
        file_queue.task_done()

def summarize():
    screenshots_contents = retrieve_contents_from_db('screenshots')
    photos_contents = retrieve_contents_from_db('photos')

    full_contents = []
    full_contents.extend(screenshots_contents)
    full_contents.extend(photos_contents)

    response = send_text_to_api(full_contents)
    print(f'response: {response}')

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    content = response['choices'][0]['message']['content']
    save_to_summary_db(timestamp, content)
    
    print(f'Summary\n{content}')
    
def start_primary_process():
    print(f'Started Primary Loop')
    
    global running, cap
    
    running = True
    
    cap = cv2.VideoCapture(0)

    screenshot_thread = Thread(target=screenshot_loop)
    screenshot_thread.start()
    photo_thread = Thread(target=photo_loop)
    photo_thread.start()
    # api_thread = Thread(target=api_loop)
    # api_thread.start()
def stop_primary_process():
    print(f'Stopped Primary Loop')
    
    global running, cap
    
    running = False
    cv2.destroyAllWindows()
    cap.release()
# endregion

# region UI Related
def update_interval(new_interval):
    global default_interval
    print(f'Updating Interval from {default_interval} to {new_interval}')
    default_interval = int(new_interval)
    save_config('default_interval', default_interval)
def update_quality_level(new_quality_val):
    global default_quality_val
    print(f'Updating Quality % from {default_quality_val} to {new_quality_val}')
    default_quality_val = str(new_quality_val)
    save_config('default_quality_val', default_quality_val)
def update_openai_api_key(new_openai_api_key):
    global default_openai_api_key
    print(f'Updating OpenAI API Key from {default_openai_api_key} to {new_openai_api_key}')
    default_openai_api_key = str(new_openai_api_key)
    save_config('default_openai_api_key', default_openai_api_key)
def update_together_api_key(new_together_api_key):
    global default_together_api_key
    print(f'Updating Together API Key from {default_together_api_key} to {new_together_api_key}')
    default_together_api_key = str(new_together_api_key)
    save_config('default_together_api_key', default_together_api_key)
def update_compression_level(new_downscale_perc):
    global default_downscale_perc
    print(f'Updating Compression % from {default_downscale_perc} to {new_downscale_perc}')
    default_downscale_perc = int(new_downscale_perc)
    save_config('default_downscale_perc', default_downscale_perc)
def update_image_model(new_image_model):
    global default_image_model
    print(f'Updating Image Model from {default_image_model} to {new_image_model}')
    default_image_model = str(new_image_model)
    save_config('default_image_model', default_image_model)
def update_text_model(new_text_model):
    global default_text_model
    print(f'Updating Text Model from {default_text_model} to {new_text_model}')
    default_text_model = str(new_text_model)
    save_config('default_text_model', default_text_model)

def on_closing():
    print("Closing application...")
    global running
    if running:
        stop_primary_process()
    root.destroy()

def create_ui():
    print(f'Building UI...\n')

    global root, default_text_model, default_image_model, default_interval, default_together_api_key, default_openai_api_key, default_downscale_perc, default_quality_val, default_system_prompt
    
    # region Initial
    main_color_100 = '#ffffff'
    main_color_500 = '#878787'
    main_color_1000 = '#141414'
    accent_color_100 = '#ab36ff'
    width = 500
    height = 600

    root = tk.Tk()
    root.config(bg=main_color_100)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.title("EYES")

    # Calculate screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate x and y position for root window
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
    # endregion

    # region Input
    frame_input = tk.Frame(root, bg=main_color_100)
    frame_input.pack(side="left", padx=(10, 5), pady=(10, 5))

    # region Config
    frame_config = tk.Frame(frame_input, bg=main_color_100)
    frame_config.pack(pady=(10, 5))
    config_label = tk.Label(frame_config, text="Config", bg=main_color_100, fg=main_color_1000, font=('Arial', 12, 'bold'))
    config_label.pack(pady=(5, 10))
    # Interval
    label_interval = tk.Label(frame_config, text="Interval", bg=main_color_100, fg=main_color_1000)
    label_interval.pack()
    interval_entry = tk.Entry(frame_config, width=30)
    interval_entry.pack()
    interval_entry.insert(0, str(default_interval))
    interval_entry.bind('<FocusOut>', lambda event: update_interval(interval_entry.get()))
    # endregion

    # region Image Options
    frame_image = tk.Frame(frame_input, bg=main_color_100)
    frame_image.pack(pady=(10, 5))
    image_options_label = tk.Label(frame_image, text="Image Options", bg=main_color_100, fg=main_color_1000, font=('Arial', 12, 'bold'))
    image_options_label.pack(pady=(10, 5))
    # API Image Quality
    label_api_image_quality = tk.Label(frame_image, text="API Image Quality", bg=main_color_100, fg=main_color_1000)
    label_api_image_quality.pack()
    image_quality_level_list = ["auto", "low", "high"]
    quality_combobox = ttk.Combobox(frame_image, values=image_quality_level_list, width=30)
    quality_combobox.set(default_quality_val)
    quality_combobox.pack()
    quality_combobox.bind("<<ComboboxSelected>>", lambda event: update_quality_level(quality_combobox.get()))
    # Saved Image Compression
    label_saved_image_compression = tk.Label(frame_image, text="Saved Image Compression", bg=main_color_100, fg=main_color_1000)
    label_saved_image_compression.pack()
    compression_level_list = [5, 15, 25, 50, 75]
    compression_combobox = ttk.Combobox(frame_image, values=compression_level_list, width=30)
    compression_combobox.set(default_downscale_perc)
    compression_combobox.pack()
    compression_combobox.bind("<<ComboboxSelected>>", lambda event: update_compression_level(compression_combobox.get()))
    # endregion

    # region Model Options
    frame_model = tk.Frame(frame_input, bg=main_color_100)
    frame_model.pack(pady=(10, 5))
    model_options_label = tk.Label(frame_model, text="Model Options", bg=main_color_100, fg=main_color_1000, font=('Arial', 12, 'bold'))
    model_options_label.pack(pady=(10, 5))
    # OpenAI API Key
    openai_api_key = tk.Label(frame_model, text="OpenAI API Key", bg=main_color_100, fg=main_color_1000)
    openai_api_key.pack()
    openai_api_key_entry = tk.Entry(frame_model, width=30, show="*")
    openai_api_key_entry.pack()
    openai_api_key_entry.insert(0, str(default_openai_api_key))
    openai_api_key_entry.bind('<FocusOut>', lambda event: update_openai_api_key(openai_api_key_entry.get()))
    # Together API Key
    together_api_key = tk.Label(frame_model, text="Together API Key", bg=main_color_100, fg=main_color_1000)
    together_api_key.pack()
    together_api_key_entry = tk.Entry(frame_model, width=30, show="*")
    together_api_key_entry.pack()
    together_api_key_entry.insert(0, str(default_together_api_key))
    together_api_key_entry.bind('<FocusOut>', lambda event: update_together_api_key(together_api_key_entry.get()))
    # Image Model
    label_image_model = tk.Label(frame_model, text="Model", bg=main_color_100, fg=main_color_1000)
    label_image_model.pack()
    image_model_list = [
        "GPT", 
        "Moondream"
    ]
    image_model_combobox = ttk.Combobox(frame_model, values=image_model_list, width=30)
    image_model_combobox.configure(background=main_color_100, foreground=main_color_1000)
    image_model_combobox.set(default_image_model)
    image_model_combobox.pack()
    image_model_combobox.bind('<FocusOut>', lambda event: update_image_model(image_model_combobox.get()))
    # Image Model
    label_text_model = tk.Label(frame_model, text="Model", bg=main_color_100, fg=main_color_1000)
    label_text_model.pack()
    text_model_list = [
        "GPT-3.5-Turbo", 
        "GPT-4-Turbo",
        "Mixtral-8x7B-Instruct-v0.1",
        "OpenHermes-Mistral-7B"
    ]
    text_model_combobox = ttk.Combobox(frame_model, values=text_model_list, width=30)
    text_model_combobox.configure(background=main_color_100, foreground=main_color_1000)
    text_model_combobox.set(default_text_model)
    text_model_combobox.pack()
    text_model_combobox.bind('<FocusOut>', lambda event: update_text_model(text_model_combobox.get()))
    # endregion
    
    # endregion

    # region Control
    frame_control = tk.Frame(root, bg=main_color_100)
    frame_control.pack(side="right", padx=(5, 10), pady=(10, 5))

    # region Buttons
    frame_button = tk.Frame(frame_control, bg=main_color_100)
    frame_button.pack(pady=(10, 5))
    start_button = tk.Button(
        frame_button, 
        text="Start",  
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, 
        width=20, height=2,
        command=lambda: start_primary_process()
    )
    start_button.grid(row=0, column=0, padx=5, pady=10)
    stop_button = tk.Button(
        frame_button, 
        text="Stop", 
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, 
        width=20, height=2,
        command=lambda: stop_primary_process()
    )
    stop_button.grid(row=1, column=0, padx=5, pady=10)
    api_call_button = tk.Button(
        frame_button, 
        text="API Call", 
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, 
        width=20, height=2,
        command=lambda: api_loop()
    )
    api_call_button.grid(row=2, column=0, padx=5, pady=10)
    summarize_button = tk.Button(
        frame_button, 
        text="Summarize", 
        bg=accent_color_100, fg=main_color_1000, borderwidth=0, highlightthickness=0, 
        width=20, height=2,
        command=lambda: summarize()
    )
    summarize_button.grid(row=3, column=0, padx=5, pady=10)
    # endregion

    # endregion

    root.mainloop()
# endregion

if __name__ == "__main__":
    print(f'Starting EYES...\n')
    load_config()
    initialize_db()
    create_ui()