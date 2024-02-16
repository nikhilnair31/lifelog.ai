import os
import io
import cv2
import time
from PIL import Image
from mss import mss

class PhotoManager:
    def __init__(self, controlManager, modelManager, databaseManager, imageManager):
        self.controlManager = controlManager
        self.modelManager = modelManager
        self.databaseManager = databaseManager
        self.imageManager = imageManager

        self.photos_folder_path = 'data/photos/'
        self.default_interval = 7
        self.default_downscale_perc = 25
        self.default_system_prompt = "What do you see?"
        self.cap = None

    def take_photo(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        _, img_encoded = cv2.imencode('.jpeg', frame)
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
            original_image_bytes_base64_encoded = self.imageManager.encode_image(original_image_bytes)
            description_text = self.modelManager.send_image_to_api(original_image_bytes_base64_encoded, self.default_system_prompt)
            
            # Save the original image to the specified path
            downscaled_image_bytes = self.imageManager.downscale_image(original_image_bytes, quality=self.default_downscale_perc)
            image_filename = f"{filename}.jpeg"
            image_path = os.path.join(self.photos_folder_path, image_filename)
            with open(image_path, 'wb') as f:
                f.write(downscaled_image_bytes)

            # Save to SQL
            self.databaseManager.save_to_photo_db(timestamp, image_filename, description_text)

            if self.controlManager.stop_event.wait(self.default_interval):
                break