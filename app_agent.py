import os
import time
import sqlite3

class AgentManager:
    def __init__(self, controlManager, modelManager, databaseManager, imageManager):
        self.controlManager = controlManager
        self.modelManager = modelManager
        self.databaseManager = databaseManager
        self.imageManager = imageManager

        self.default_interval = 60

        self.model_name = "gpt-3.5-turbo-0125"
        self.default_system_prompt = """
            You are the user's helper who is inside their desktop.
            You are provided the following:
            - A running summary of the user's activity
            - Descriptions of their desktop's screenshot
            - Descriptions of their webcam's images 
            - Transcripts of their desktop's audio
            Summarize with cool details. Be precise.
        """
    
    def agent_live_summarizer(self):
        print(f'Agent Loop\n')

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        to_timestamp, screenshots_description_text_rows, photos_description_text_rows, audio_transcript_text_rows = self.databaseManager.retrieve_all_sources_text_content_for_livesummary(timestamp)
        last_summary = self.databaseManager.retrieve_last_summary_for_livesummary()

        screenshots_description_text = '\n'.join(screenshots_description_text_rows)
        photos_description_text = '\n'.join(photos_description_text_rows)
        audio_transcript_text = '\n'.join(audio_transcript_text_rows)

        default_user_prompt = f"Running Summary:\n{last_summary}\nScreenshots Descriptions:\n{screenshots_description_text}\nPhotos Descriptions:\n{photos_description_text}\nAudio Transcripts:\n{audio_transcript_text}"
        
        # Take all text and summarize
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": self.default_system_prompt
                },
                {
                    "role": "user",
                    "content": default_user_prompt
                }
            ],
            "max_tokens": 256,
            "temperature": 0.1
        }
        summarize_text = self.modelManager.call_together_api("gpt", payload)

        # Save to SQL
        self.databaseManager.save_to_summary_db(timestamp, to_timestamp, timestamp, str(payload), summarize_text)
        
    def agent_loop(self):
        print(f'Agent Loop\n')

        while self.controlManager.is_running():        
            print(f'Running Agent Loop')
            
            self.agent_live_summarizer()
            
            if self.controlManager.stop_event.wait(self.default_interval):
                break