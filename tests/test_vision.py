import os
import time
import json
import base64
import requests

config_file = 'config.json'
default_openai_api_key = ''
default_system_prompt = "What do you see? Be precise. You have the screenshots of my screen! Tell what you see on the screen and text you see in details! It can be rick and morty series, terminal, twitter, vs code, and other! answer with cool details! Answer in 20 words max! Make a story about my screenshot day out of it! If you can't see make best guess!"

def load_config():
    global config_file, default_openai_api_key
    with open(config_file, 'r') as file:
        config_data = json.load(file)
        print(f"Config file : {config_data}\n")
        default_openai_api_key = config_data.get('default_openai_api_key', default_openai_api_key)

def call_gpt4v_api(image_bytes):
    """Send the screenshot to the API and return the response."""

    print(f'Calling OpenAI API...')
    
    start_time = time.time()  # Capture start time

    base64_image = encode_image(image_bytes)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {default_openai_api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": default_system_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print(f'Received response in {elapsed_time:.2f} seconds.')  # Print the elapsed time to two decimal places
    
    return response.json()

def encode_image(image_bytes):
    """Encode image bytes to base64."""
    return base64.b64encode(image_bytes).decode('utf-8')

load_config()
folder_path = 'sample/'
files = os.listdir(folder_path)
for file in files:
    file_path = os.path.join(folder_path, file)
    with open(file_path, 'rb') as file:
        image_bytes = file.read()
    response = call_gpt4v_api(image_bytes)
    print(f'file_path: {file_path}\nresponse\n{response}\n{"-"*25}')