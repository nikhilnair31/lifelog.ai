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
        self.default_system_prompt = "You have the descriptions of my desktop's screenshot, the descriptions of my webcam images and the transcripts of my desktop's audio. Summarize with cool details. Be precise."
    
    # FIXME: Currently just summarize b/w from-to timestamps but ideally should be building onto the previous summary
    def agent_summarize(self):
        print(f'Agent Loop\n')

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        to_timestamp, screenshots_description_text_rows, photos_description_text_rows, audio_transcript_text_rows = self.databaseManager.retrieve_contents_for_livesummary(timestamp)
        
        screenshots_description_text = '\n'.join(screenshots_description_text_rows)
        photos_description_text = '\n'.join(photos_description_text_rows)
        audio_transcript_text = '\n'.join(audio_transcript_text_rows)
        
        # Pass OCR through LLM
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": self.default_system_prompt
                },
                {
                    "role": "user",
                    "content": f"Screenshots Descriptions:\n{screenshots_description_text}\nPhotos Descriptions:\n{photos_description_text}\nAudio Transcripts:\n{audio_transcript_text}"
                }
            ],
            "max_tokens": 256,
            "temperature": 0.1
        }
        # print(f'payload\n{payload}')
        summarize_text = self.modelManager.call_together_api("gpt", payload)
        # print(f'Summary\n{summarize_text}')

        # Save to SQL
        self.databaseManager.save_to_summary_db(timestamp, to_timestamp, timestamp, str(payload), summarize_text)
        
    def agent_loop(self):
        print(f'Agent Loop\n')

        while self.controlManager.is_running():        
            print(f'Running Agent Loop')
            
            self.agent_summarize()
            
            if self.controlManager.stop_event.wait(self.default_interval):
                break