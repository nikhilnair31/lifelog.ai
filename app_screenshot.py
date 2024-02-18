import os
import io
import cv2
import time
import pytesseract
from PIL import Image
from mss import mss

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ScreenshotManager:
    def __init__(self, configManager, controlManager, modelManager, databaseManager, mediaManager):
        self.configManager = configManager
        self.controlManager = controlManager
        self.modelManager = modelManager
        self.databaseManager = databaseManager
        self.mediaManager = mediaManager

        self.screenshot_loop_time_in_min = self.configManager.get_config("screenshot_loop_time_in_min") * 60
        self.screenshot_text_model = self.configManager.get_config("screenshot_text_model")
        self.screenshot_compression_perc = self.configManager.get_config("screenshot_compression_perc")

        self.screenshots_folder_path = 'data/screenshots/'
        self.default_system_prompt = "What do you see? Be precise. You have the OCR text contents of my Windows desktop screenshots. Tell what you see on the screen and text you see in details. It can be a youtube video, rick and morty series, terminal, twitter, vs code, and many others. answer with cool details. If you can't see make best guess."

    def take_screenshot(self):
        with mss() as sct:
            monitor = sct.monitors[0]
            width = min(3840, monitor['width'])
            height = min(1080, monitor['height'])
            sct_img = sct.grab({
                "top": monitor["top"], 
                "left": monitor["left"], 
                "width": width, 
                "height": height
            })
            screenshot = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    
    def extract_text_from_image_tesseract(self, negated_image_bytes):
        try:
            with Image.open(io.BytesIO(negated_image_bytes)) as img:
                extracted_text = pytesseract.image_to_string(img)
                return extracted_text
        except Exception as e:
            print("Error:", e)
            return ''
    
    def screenshot_loop(self):
        print(f'Screenshot Loop\n')

        if not os.path.exists(self.screenshots_folder_path):
            os.makedirs(self.screenshots_folder_path)

        while self.controlManager.is_running():        
            print(f'Running Screenshot Loop')

            # Pull data
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            filename = time.strftime('%Y-%m-%d-%H-%M-%S')
            original_image_bytes = self.take_screenshot()
            
            # Pass through OCR
            negated_image_bytes = self.mediaManager.negate_image(original_image_bytes)
            ocr_text = self.extract_text_from_image_tesseract(negated_image_bytes)
            
            # Pass OCR through LLM
            payload = {
                "model": "openchat/openchat-3.5-1210",
                "messages": [
                    {
                        "role": "system",
                        "content": self.default_system_prompt
                    },
                    {
                        "role": "user",
                        "content": ocr_text
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.1
            }
            description_text = self.modelManager.send_text_to_together_api("together", payload)
            
            # Save compressed image
            downscaled_image_bytes = self.mediaManager.downscale_image(original_image_bytes, quality=self.screenshot_compression_perc)
            image_filename = f"{filename}.jpeg"
            image_path = os.path.join(self.screenshots_folder_path, image_filename)
            with open(image_path, 'wb') as f:
                f.write(downscaled_image_bytes)

            # Save to SQL
            self.databaseManager.save_to_screenshot_db(timestamp, image_filename, ocr_text, description_text)

            if self.controlManager.stop_event.wait(self.screenshot_loop_time_in_min):
                break