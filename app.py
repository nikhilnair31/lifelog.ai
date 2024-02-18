import tkinter as tk
from tkinter import ttk
from threading import Thread

from app_helper import ControlManager, ModelManager, MediaManager
from app_config import ConfigurationManager
from app_db import DatabaseManager
from app_screenshot import ScreenshotManager
from app_audio import AudioManager
from app_photo import PhotoManager
from app_agent import AgentManager
from app_ui import UIManager

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
    mediaManager = MediaManager(

    )
    modelManager = ModelManager(
        configManager
    )
    agentManager = AgentManager(
        configManager, controlManager, modelManager, databaseManager, mediaManager
    )
    screenshotManager = ScreenshotManager(
        configManager, controlManager, modelManager, databaseManager, mediaManager
    )
    photoManager = PhotoManager(
        configManager, controlManager, modelManager, databaseManager, mediaManager
    )
    audioManager = AudioManager(
        configManager, controlManager, modelManager, databaseManager, mediaManager
    )

    app = UIManager(
        configManager, controlManager,
        start_primary_process, stop_primary_process
    )
    app.run()