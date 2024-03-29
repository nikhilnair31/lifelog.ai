import os
import io
import json
import time
import base64
import requests
import tempfile
import threading
from PIL import Image
from openai import OpenAI
from gradio_client import Client
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

class ControlManager:
    def __init__(self):
        self._running = False
        self.stop_event = threading.Event()

    def start(self):
        self._running = True
    def stop(self):
        self._running = False
        self.stop_event.set()

    def is_running(self):
        return self._running

class ModelManager:
    def __init__(self, configManager):
        self.configManager = configManager

        self.openai_api_key = self.configManager.get_config("openai_api_key")
        self.together_api_key = self.configManager.get_config("together_api_key")
        self.deepgram_api_key = self.configManager.get_config("deepgram_api_key")

    def send_image_to_api(self, base64_encoded_image, image_model_name, system_prompt):
        """Determine which API to call based on the model selection and send the screenshot."""

        print(f'Sending Images to API...')
        
        if image_model_name == "gpt-4-turbo-preview":
            response = self.call_gpt4v_api(base64_encoded_image, system_prompt)
        elif image_model_name == "moondream":
            response = self.call_moondream_api(base64_encoded_image, system_prompt)
        else:
            print(f"Invalid model selection: {image_model_name}")
            return None
        
        return response
    def call_gpt4v_api(self, base64_encoded_image, system_prompt):
        print(f'Calling GPT4V API...')
        
        start_time = time.time()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
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
                                "url": f"data:image/jpeg;base64,{base64_encoded_image}",
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
        print(f'Received GPT4V response in {elapsed_time:.2f} seconds.')
        
        return response.json()['choices'][0]['message']['content']
    def call_moondream_api(self, base64_encoded_image, system_prompt):
        print(f'Calling Moondream API...')
        
        start_time = time.time()

        try:
            # Decode the base64 string to bytes
            image_bytes = base64.b64decode(base64_encoded_image)
            # Load the image from bytes for a sanity check or manipulation if needed
            img = Image.open(io.BytesIO(image_bytes))

            # Save the image temporarily
            # FIXME: Fix this problem
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg') as tmpfile:
                img.save(tmpfile, format="JPEG")
                tmpfile_path = tmpfile.name
                img.close()

            # Initialize the Gradio client with your Moondream API URL
            client = Client("https://niknair31-moondream1.hf.space/--replicas/frktd/")

            result = client.predict(
                tmpfile_path,
                system_prompt,  
                api_name="/answer_question"
            )
        
            elapsed_time = time.time() - start_time
            print(f'Received Moondream response in {elapsed_time:.2f} seconds.')

            return result
        except Exception as e:
            print("An error occurred while calling Moondream API:", str(e))
            return ""
        finally:
            # Delay the deletion to here, ensuring all references are released
            if os.path.exists(tmpfile_path):
                os.unlink(tmpfile_path)

    def send_text_to_llm_api(self, payload):
        print(f'Calling LLM API...')
        
        start_time = time.time()
        
        model_name = payload["model"]
        # print(f"model_name: {model_name}")
        model_source = model_name.split('/')[0]
        # print(f"model_source: {model_source}")
        actual_model_name = model_name.replace(model_source+"/", "")
        # print(f"actual_model_name: {actual_model_name}")

        if "local" in model_source:
            url = "http://localhost:1234/v1/chat/completions"
            headers = {
                "Content-Type": "application/json"
            }
        else:
            if "gpt" in actual_model_name:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                }
            else:
                url = "https://api.together.xyz/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.together_api_key}"
                }

        payload["model"] = actual_model_name
        # print(f"payload: {payload}")

        response = requests.post(url, headers=headers, json=payload)
        # print(f"response.json()\n{response.json()}")
        
        elapsed_time = time.time() - start_time
        print(f'Received Together response in {elapsed_time:.2f} seconds.')
        
        return response.json()['choices'][0]['message']['content']

    def send_audio_to_api(self, audio_path, audio_model):
        """Determine which API to call based on the model selection and send the screenshot."""

        print(f'Sending Audio to API...')
        
        if audio_model == "deepgram":
            response = self.call_deepgram_api(audio_path)
        elif audio_model == "whisper":
            response = self.call_whisper_api(audio_path)
        else:
            print(f"Invalid model selection: {audio_model}")
            return None
        
        return response
    def call_deepgram_api(self, audio_path):
        print(f'Calling Deepgram API...')

        start_time = time.time()

        deepgram = DeepgramClient(self.deepgram_api_key)
        
        with open(audio_path, "rb") as file:
            buffer_data = file.read()
        payload: FileSource = {
            "buffer": buffer_data,
        }
        options = PrerecordedOptions(
            model="nova-2-general"
            # smart_format=True,
            # diarize=True,
            # dictation=True,
            # filler_words=True,
            # profanity_filter=False,
            # punctuate=True
            # summarize="v2"
        )

        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        
        elapsed_time = time.time() - start_time
        print(f'Received Deepgram response in {elapsed_time:.2f} seconds.')

        return response["results"]["channels"][0]["alternatives"][0]["transcript"]
    def call_whisper_api(self, audio_path):
        print(f'Calling Whisper API...')

        start_time = time.time()
        client = OpenAI(self.openai_api_key)

        audio_file= open(audio_path, "rb")
        response = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        
        elapsed_time = time.time() - start_time
        print(f'Received Deepgram response in {elapsed_time:.2f} seconds.')

        return response["text"]

class MediaManager:
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