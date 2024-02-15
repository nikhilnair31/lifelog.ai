import os
import io
import time
import base64
import requests
from PIL import Image

# region ControlManager
class ControlManager:
    def __init__(self):
        self._running = False

    def start(self):
        self._running = True
    def stop(self):
        self._running = False

    def is_running(self):
        return self._running
# endregion

# region ModelManager
class ModelManager:
    def __init__(self, default_openai_api_key, default_together_api_key, 
            default_text_model, default_image_model):
        self.default_openai_api_key = default_openai_api_key
        self.default_together_api_key = default_together_api_key
        self.default_text_model = default_text_model
        self.default_image_model = default_image_model

    def send_image_to_api(self, image_bytes, system_prompt):
        """Determine which API to call based on the model selection and send the screenshot."""

        print(f'Sending Images to API...')
        
        if self.default_image_model == "GPT":
            response = self.call_gpt4v_api(image_bytes, system_prompt)
        elif self.default_image_model == "Moondream":
            response = self.call_moondream_api(image_bytes, system_prompt)
        else:
            print(f"Invalid model selection: {self.default_image_model}")
            return None
        
        return response
    def call_gpt4v_api(self, image_bytes, system_prompt):
        """Send the screenshot to the API and return the response."""

        print(f'Calling GPT4V API...')
        
        # Capture start time
        start_time = time.time()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.default_openai_api_key}"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_bytes}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        # print(response.json())
        
        # Time calculation
        elapsed_time = time.time() - start_time
        print(f'Received response in {elapsed_time:.2f} seconds.')
        
        return response.json()['choices'][0]['message']['content']
    def call_moondream_api(self, image_bytes, system_prompt):
        print(f'Calling Moondream API...')

        # Load the image from bytes for a sanity check or manipulation if needed
        img = Image.open(io.BytesIO(image_bytes))

        # Save the image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg') as tmpfile:
            img.save(tmpfile, format="JPEG")
            tmpfile_path = tmpfile.name

        # Initialize the Gradio client with your Moondream API URL
        client = Client("https://vikhyatk-moondream1.hf.space/--replicas/1hkz3/")

        # Make the prediction (API call)
        try:
            result = client.predict(
                tmpfile_path,
                system_prompt,  
                api_name="/answer_question"
            )
            return result
        except Exception as e:
            print("An error occurred while calling Moondream API:", str(e))
            return ""
        finally:
            # Optionally delete the temp file if not needed anymore
            os.unlink(tmpfile_path)

    def send_text_to_api(self, text_list):
        """Determine which API to call based on the model selection and send the screenshot."""

        print(f'Sending Text to API...')
        
        if default_text_model == "GPT-3.5-Turbo":
            response = call_together_api('gpt-3.5-turbo', "gpt", text_list)
        elif default_text_model == "GPT-4-Turbo":
            response = call_together_api('gpt-4-turbo-preview', "gpt", text_list)
        elif default_text_model == "Mixtral-8x7B-Instruct-v0.1":
            response = call_together_api('mistralai/Mixtral-8x7B-Instruct-v0.1', "together", text_list)
        elif default_text_model == "OpenHermes-Mistral-7B":
            response = call_together_api('teknium/OpenHermes-2p5-Mistral-7B', "together", text_list)
        else:
            print(f"Invalid model selection: {default_text_model}")
            return None
        
        return response
    def call_together_api(self, source, payload):
        """Send the contents to the API and return the response."""

        print(f'Calling Together API...')
        
        start_time = time.time()
        
        if source == "gpt":
            url = "https://api.openai.com/v1/chat/completions"
            api_key = self.default_openai_api_key
        else:
            url = "https://api.together.xyz/v1/chat/completions"
            api_key = self.default_together_api_key

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        # print(response.json())
        
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        print(f'Received response in {elapsed_time:.2f} seconds.')  # Print the elapsed time to two decimal places
        
        return response.json()['choices'][0]['message']['content']
# endregion

# region ImageManager
class ImageManager:
    def __init__(self):
        pass

    def downscale_image(self, image_bytes, quality=90):
        try:
            print('Downscaling Image...')
            img = Image.open(io.BytesIO(image_bytes))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=quality)
            return img_byte_arr.getvalue()
        except Exception as e:
            print("Downscaling Image Error:", e)
            return None
        
    def negate_image(self, image_bytes):
        try:
            print('Negating Image...')
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Convert image to grayscale
                grayscale_img = img.convert('L')
                # Invert the grayscale image
                inverted_img = Image.eval(grayscale_img, lambda x: 255 - x)
                # Save the inverted image
                output_img_byte_arr = io.BytesIO()
                inverted_img.save(output_img_byte_arr, format='JPEG')
            return output_img_byte_arr.getvalue()
        except Exception as e:
            print("Negate Image Error:", e)
            return None

    def encode_image(self, image_bytes):
        """Encode image bytes to base64."""
        try:
            return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            print("Encode Image Error:", e)
            return None
# endregion