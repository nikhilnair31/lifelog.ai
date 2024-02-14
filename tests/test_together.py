import time
import json
import requests

config_file = 'config.json'
default_together_api_key = ''

def load_config():
    global config_file, default_together_api_key
    with open(config_file, 'r') as file:
        config_data = json.load(file)
        print(f"Config file : {config_data}\n")
        default_together_api_key = config_data.get('default_together_api_key', default_together_api_key)

def call_together_api(contents):
    """Send the contents to the API and return the response."""

    print(f'Calling Together API...')
    
    start_time = time.time()  # Capture start time

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {default_together_api_key}"
    }
    payload = {
        "model": "openchat/openchat-3.5-1210",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. You have received the description of screenshots and webcam images from the user. You need to summarize the day."
            },
            {
                "role": "user",
                "content": "Summarize today's events. Format it nicely in bullet poitns in HTML. Your WHOLE answer must be in HTML."
            },
            {
                "role": "assistant",
                "content": "\n".join(contents)
            }
        ]
    }
    
    response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
    print(response)

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print(f'Received response in {elapsed_time:.2f} seconds.')  # Print the elapsed time to two decimal places
    
    print(response.json())

load_config()
call_together_api(['hi'])