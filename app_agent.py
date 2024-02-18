import os
import time
import sqlite3

class AgentManager:
    def __init__(self, configManager, controlManager, modelManager, databaseManager, mediaManager):
        self.configManager = configManager
        self.controlManager = controlManager
        self.modelManager = modelManager
        self.databaseManager = databaseManager
        self.mediaManager = mediaManager

        self.agent_livesummary_loop_time_in_min = self.configManager.get_config("agent_livesummary_loop_time_in_min") * 60
        self.agent_livesummary_text_model = self.configManager.get_config("agent_livesummary_text_model")

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
        print(f'Live Summarizer\n')

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        to_timestamp, screenshots_description_text_rows, photos_description_text_rows, audio_transcript_text_rows = self.databaseManager.retrieve_all_sources_text_content_for_livesummary(timestamp)
        last_summary = self.databaseManager.retrieve_last_summary_for_livesummary()

        # FIXME: Figure out how to improve this
        len_filter = 100
        screenshots_description_text = '\n'.join(screenshots_description_text_rows[:len_filter])
        photos_description_text = '\n'.join(photos_description_text_rows[:len_filter])
        audio_transcript_text = '\n'.join(audio_transcript_text_rows[:len_filter])

        default_user_prompt = f"Running Summary:\n{last_summary}\nScreenshots Descriptions:\n{screenshots_description_text}\nPhotos Descriptions:\n{photos_description_text}\nAudio Transcripts:\n{audio_transcript_text}"
        
        # Take all text and summarize
        payload = {
            "model": self.agent_livesummary_text_model,
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
        print(f"payload: {payload}")
        summarize_text = self.modelManager.send_text_to_together_api(payload)

        # Save to SQL
        self.databaseManager.save_to_summary_db(timestamp, to_timestamp, timestamp, str(payload), summarize_text)
        
    def agent_loop(self):
        print(f'Agent Loop\n')

        while self.controlManager.is_running():        
            print(f'Running Agent Loop')
            
            self.agent_live_summarizer()
            
            if self.controlManager.stop_event.wait(self.agent_livesummary_loop_time_in_min):
                break