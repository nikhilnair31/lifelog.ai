# region Packages
import tkinter as tk
from tkinter import ttk
from threading import Thread

from app_helper import ControlManager, ModelManager, ImageManager
from app_config import ConfigurationManager
from app_db import DatabaseManager
from app_screenshot import ScreenshotManager
from app_photo import PhotoManager
# endregion

# region Setup
photos_folder_path = 'data/photos/'
screenshots_folder_path = 'data/screenshots/'
sql_folder_path = 'data/sql/'

db_path = 'data/sql/data.db'

default_text_model = 'GPT-3.5-Turbo'
default_image_model = 'GPT'
default_interval = 5
default_openai_api_key = ''
default_together_api_key = ''
default_downscale_perc = 25
default_quality_val = 'low'
default_system_prompt = "What do you see? Be precise. You have the screenshots of my screen! Tell what you see on the screen and text you see in details! It can be rick and morty series, terminal, twitter, vs code, and other! answer with cool details! Answer in 20 words max! Make a story about my screenshot day out of it! If you can't see make best guess!"

image_quality_level_list = [
    "auto", "low", "high"
]
compression_level_list = [
    5, 15, 25, 50, 75
]
image_model_list = [
    "GPT", 
    "Moondream"
]
text_model_list = [
    "GPT-3.5-Turbo", 
    "GPT-4-Turbo",
    "Mixtral-8x7B-Instruct-v0.1",
    "OpenHermes-Mistral-7B",
    "openchat/openchat-3.5-1210"
]
# endregion

# region Primary Related 
def start_primary_process():
    print(f'Started!\n')

    controlManager.start()
    screenshot_thread = Thread(target=screenshotManager.screenshot_loop)
    screenshot_thread.start()
    photo_thread = Thread(target=photoManager.photo_loop)
    photo_thread.start()

def stop_primary_process():
    print(f'Stopped!\n')
    
    controlManager.stop()
# endregion

# region UI Related
def update_interval(new_interval):
    print(f'Updating Interval from {default_interval} to {new_interval}')
    default_interval = int(new_interval)
    save_config('default_interval', default_interval)
def update_quality_level(new_quality_val):
    print(f'Updating Quality % from {default_quality_val} to {new_quality_val}')
    default_quality_val = str(new_quality_val)
    save_config('default_quality_val', default_quality_val)
def update_openai_api_key(new_openai_api_key):
    print(f'Updating OpenAI API Key from {default_openai_api_key} to {new_openai_api_key}')
    default_openai_api_key = str(new_openai_api_key)
    save_config('default_openai_api_key', default_openai_api_key)
def update_together_api_key(new_together_api_key):
    print(f'Updating Together API Key from {default_together_api_key} to {new_together_api_key}')
    default_together_api_key = str(new_together_api_key)
    save_config('default_together_api_key', default_together_api_key)
def update_compression_level(new_downscale_perc):
    print(f'Updating Compression % from {default_downscale_perc} to {new_downscale_perc}')
    default_downscale_perc = int(new_downscale_perc)
    save_config('default_downscale_perc', default_downscale_perc)
def update_image_model(new_image_model):
    print(f'Updating Image Model from {default_image_model} to {new_image_model}')
    default_image_model = str(new_image_model)
    save_config('default_image_model', default_image_model)
def update_text_model(new_text_model):
    print(f'Updating Text Model from {default_text_model} to {new_text_model}')
    default_text_model = str(new_text_model)
    save_config('default_text_model', default_text_model)

def on_closing():
    print("Closing application...")
    if controlManager.is_running():
        stop_primary_process()
    root.destroy()

def create_ui():
    print(f'Building UI...\n')

    global root

    # region Initial
    main_color_100 = '#ffffff'
    main_color_500 = '#878787'
    main_color_1000 = '#141414'
    accent_color_100 = '#ab36ff'
    width = 400
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
    quality_combobox = ttk.Combobox(frame_image, values=image_quality_level_list, width=30)
    quality_combobox.set(default_quality_val)
    quality_combobox.pack()
    quality_combobox.bind("<<ComboboxSelected>>", lambda event: update_quality_level(quality_combobox.get()))
    # Saved Image Compression
    label_saved_image_compression = tk.Label(frame_image, text="Saved Image Compression", bg=main_color_100, fg=main_color_1000)
    label_saved_image_compression.pack()
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
    image_model_combobox = ttk.Combobox(frame_model, values=image_model_list, width=30)
    image_model_combobox.configure(background=main_color_100, foreground=main_color_1000)
    image_model_combobox.set(default_image_model)
    image_model_combobox.pack()
    image_model_combobox.bind('<FocusOut>', lambda event: update_image_model(image_model_combobox.get()))
    # Image Model
    label_text_model = tk.Label(frame_model, text="Model", bg=main_color_100, fg=main_color_1000)
    label_text_model.pack()
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

    configManager = ConfigurationManager()
    default_openai_api_key, default_together_api_key, default_text_model, default_image_model, default_downscale_perc, default_quality_val, default_interval = configManager.load_config()

    controlManager = ControlManager()
    imageManager = ImageManager(

    )
    databaseManager = DatabaseManager(
        db_path, sql_folder_path
    )
    modelManager = ModelManager(
        default_openai_api_key, default_together_api_key,
        default_text_model, default_image_model
    )
    screenshotManager = ScreenshotManager(
        controlManager, modelManager, databaseManager, imageManager
    )
    photoManager = PhotoManager(
        controlManager, modelManager, databaseManager, imageManager
    )

    databaseManager.initialize_db()
    
    create_ui()