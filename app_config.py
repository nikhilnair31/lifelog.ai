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