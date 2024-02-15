import json

# region ConfigurationManager
default_openai_api_key = ''
default_together_api_key = ''
default_text_model = 'GPT-3.5-Turbo'
default_image_model = 'GPT'
default_system_prompt = """
What do you see? Be precise. You have the screenshots of my screen! Tell what you see on the screen and text you see in details! It can be rick and morty series, terminal, twitter, vs code, and other! answer with cool details! Answer in 20 words max! Make a story about my screenshot day out of it! If you can't see make best guess!
"""
default_downscale_perc = 25
default_quality_val = 'low'
default_interval = 5

class ConfigurationManager:
    def __init__(self):
        self.config_file = 'config.json'

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                config_data = json.load(file)
                print(f"Config file : {config_data}\n")

                default_openai_api_key = config_data.get('default_openai_api_key', '')
                default_together_api_key = config_data.get('default_together_api_key', '')
                default_text_model = config_data.get('default_text_model', '')
                default_image_model = config_data.get('default_image_model', '')
                default_system_prompt = config_data.get('default_system_prompt', '')
                default_downscale_perc = config_data.get('default_downscale_perc', '')
                default_quality_val = config_data.get('default_quality_val', '')
                default_interval = config_data.get('default_interval', '')

                return default_openai_api_key, default_together_api_key, default_text_model, default_image_model, default_system_prompt, default_downscale_perc, default_quality_val, default_interval
        
        except FileNotFoundError:
            print("Config file not found. Creating empty and using defaults.")
            with open(self.config_file, 'w') as file:
                json.dump({
                    'default_openai_api_key': self.default_openai_api_key,
                    'default_together_api_key': self.default_together_api_key,
                    'default_text_model': self.default_text_model,
                    'default_image_model': self.default_image_model,
                    'default_system_prompt': self.default_system_prompt,
                    'default_downscale_perc': self.default_downscale_perc,
                    'default_quality_val': self.default_quality_val,
                    'default_interval': self.default_interval,
                }, file)
                pass
        
        except Exception as e:
            print("Error loading config file:", e)

    def save_config(self, key, new_val):
        try:
            # Open config file and load it into a dict
            with open(self.config_file, 'r') as file:
                config_data = json.load(file)
            # Update dict's value by key
            config_data[key] = new_val
            # Rewrite dict into config file
            with open(self.config_file, 'w') as outfile:
                json.dump(config_data, outfile)
        
        except Exception as e:
            print("Error saving config file:", e)
# endregion