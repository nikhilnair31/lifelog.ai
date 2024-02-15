import json

# region ConfigurationManager
default_openai_api_key = ''
default_together_api_key = ''
default_text_model = 'GPT-3.5-Turbo'
default_image_model = 'GPT'
default_downscale_perc = 25
default_quality_val = 'low'
default_interval = 5

# FIXME: Update to make user's UI changes reflect here 
class ConfigurationManager:
    def __init__(self):
        self.config_file = 'config.json'

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                config_data = json.load(file)
                print(f"Config File Contents\n{config_data}\n")

                default_openai_api_key = config_data.get('default_openai_api_key', '')
                default_together_api_key = config_data.get('default_together_api_key', '')
                default_text_model = config_data.get('default_text_model', '')
                default_image_model = config_data.get('default_image_model', '')
                default_downscale_perc = config_data.get('default_downscale_perc', '')
                default_quality_val = config_data.get('default_quality_val', '')
                default_interval = config_data.get('default_interval', '')

            return default_openai_api_key, default_together_api_key, default_text_model, default_image_model, default_downscale_perc, default_quality_val, default_interval

        except FileNotFoundError:
            print("Config file not found. Creating empty and using defaults.")
            
            with open(self.config_file, 'w') as file:
                json.dump({
                    'default_openai_api_key': default_openai_api_key,
                    'default_together_api_key': default_together_api_key,
                    'default_text_model': default_text_model,
                    'default_image_model': default_image_model,
                    'default_downscale_perc': default_downscale_perc,
                    'default_quality_val': default_quality_val,
                    'default_interval': default_interval,
                }, file)
            
            return default_openai_api_key, default_together_api_key, default_text_model, default_image_model, default_downscale_perc, default_quality_val, default_interval
        
        except Exception as e:
            print("Error loading config file:", e)
            return default_openai_api_key, default_together_api_key, default_text_model, default_image_model, default_downscale_perc, default_quality_val, default_interval

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