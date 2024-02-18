import json

# region ConfigurationManager
class ConfigurationManager:
    def __init__(self):
        self.config_file = 'config.json'
        self.config_data = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.config_data = json.load(file)
        except FileNotFoundError:
            self.config_data = {
                'openai_api_key': '',
                'together_api_key': '',
                'deepgram_api_key': '',

                "screenshot_loop_time_in_min": 2,
                "screenshot_text_model": "openchat/openchat-3.5-1210",
                "screenshot_compression_perc": 25,
                "screenshot_enabled": true,
                
                "photo_loop_time_in_min": 20,
                "photo_image_model": "gpt-4-turbo-preview",
                "photo_image_quality_val": "low",
                "photo_compression_perc": 25,
                "photo_enabled": true,

                "audio_loop_time_in_min": 5,
                "audio_audio_model": "deepgram",
                "audio_compression_perc": 25,
                "audio_enabled": true,

                "agent_livesummary_loop_time_in_min": 10,
                "agent_livesummary_text_model": "gpt-3.5-turbo"
            }
            self.save_all_config()  # Save defaults if file not found
        except Exception as e:
            print("Error loading config file:", e)

    def get_config(self, key):
        return self.config_data.get(key)

    def save_config(self, key, new_val):
        self.config_data[key] = new_val
        self.save_all_config()

    def save_all_config(self):
        try:
            with open(self.config_file, 'w') as outfile:
                json.dump(self.config_data, outfile)
        except Exception as e:
            print("Error saving config file:", e)
# endregion