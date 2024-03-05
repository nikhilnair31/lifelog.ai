import os
import io
import cv2
import time
from PIL import Image
from mss import mss

class PhotoManager:
    def __init__(self, configManager, controlManager, modelManager, databaseManager, mediaManager):
        self.configManager = configManager
        self.controlManager = controlManager
        self.modelManager = modelManager
        self.databaseManager = databaseManager
        self.mediaManager = mediaManager

        self.photo_loop_time_in_min = self.configManager.get_config("photo_loop_time_in_min") * 60
        self.photo_image_model = self.configManager.get_config("photo_image_model")
        self.photo_compression_perc = self.configManager.get_config("photo_compression_perc")

        self.photos_folder_path = 'data/photos/'
        # FIXME: Compare prompts for moondream API
        self.default_system_prompt = "Describe the image in detail"
        self.cap = None

    def take_photo(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            time.sleep(2)
        
        ret, frame = self.cap.read()
        
        # Check if the frame was successfully captured
        if not ret or frame is None:
            print("Failed to capture frame")
            return None

        ret, img_encoded = cv2.imencode('.jpeg', frame)
        if not ret:
            print("Failed to encode frame")
            return None  # or handle the error as needed

        return img_encoded.tobytes()
    
    def photo_loop(self):
        print(f'Photo Loop\n')

        if not os.path.exists(self.photos_folder_path):
            os.makedirs(self.photos_folder_path)

        while self.controlManager.is_running():        
            print(f'Running Photo Loop')

            # Pull data
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            filename = time.strftime('%Y-%m-%d-%H-%M-%S')
            original_image_bytes = self.take_photo()
            
            # Pass through Vision LLM
            original_image_bytes_base64_encoded = self.mediaManager.encode_image(original_image_bytes)
            description_text = self.modelManager.send_image_to_api(original_image_bytes_base64_encoded, self.photo_image_model, self.default_system_prompt)
            
            # Save the original image to the specified path
            downscaled_image_bytes = self.mediaManager.downscale_image(original_image_bytes, quality=self.photo_compression_perc)
            image_filename = f"{filename}.jpeg"
            image_path = os.path.join(self.photos_folder_path, image_filename)
            with open(image_path, 'wb') as f:
                f.write(downscaled_image_bytes)

            # Save to SQL
            self.databaseManager.save_to_photo_db(timestamp, image_filename, description_text)

            if self.controlManager.stop_event.wait(self.photo_loop_time_in_min):
                break