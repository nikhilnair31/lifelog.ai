# region Packages
import tkinter as tk
from tkinter import ttk
from threading import Thread

from app_helper import ControlManager, ModelManager, ImageManager
from app_config import ConfigurationManager
from app_db import DatabaseManager
from app_screenshot import ScreenshotManager
from app_audio import AudioManager
from app_photo import PhotoManager
from app_agent import AgentManager
from app_ui import UIManager
# endregion

# region Setup
image_model_list = [
    "gpt-4-turbo-preview", 
    "moondream"
]
text_model_list = [
    "gpt-3.5-turbo", 
    "gpt-4-turbo",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "teknium/OpenHermes-2p5-Mistral-7B",
    "openchat/openchat-3.5-1210"
]
audio_model_list = [
    "deepgram",
    "whisper"
]
image_quality_list = [
    "auto", "high", "low"
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
    audio_thread = Thread(target=audioManager.audio_loop)
    audio_thread.start()
    agent_thread = Thread(target=agentManager.agent_loop)
    agent_thread.start()

def stop_primary_process():
    print(f'Stopped!\n')
    
    controlManager.stop()
# endregion

if __name__ == "__main__":
    print(f'Starting EYES...\n')

    configManager = ConfigurationManager()

    databaseManager = DatabaseManager()
    databaseManager.initialize_db()

    controlManager = ControlManager()
    imageManager = ImageManager(

    )
    modelManager = ModelManager(
        configManager
    )
    agentManager = AgentManager(
        controlManager, modelManager, databaseManager, imageManager
    )
    screenshotManager = ScreenshotManager(
        controlManager, modelManager, databaseManager, imageManager
    )
    photoManager = PhotoManager(
        controlManager, modelManager, databaseManager, imageManager
    )
    audioManager = AudioManager(
        controlManager, modelManager, databaseManager, imageManager
    )

    app = UIManager(
        configManager, controlManager,
        image_model_list, text_model_list, audio_model_list, image_quality_list
    )
    app.run()