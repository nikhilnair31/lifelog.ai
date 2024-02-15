# region Packages
import os
import io
import cv2
import requests
import pyautogui
from mss import mss
from PIL import Image
from screeninfo import get_monitors
# endregion

# region Image Related
def take_screenshot():
    with mss() as sct:
        # The first entry of sct.monitors is the entire screen
        monitor = sct.monitors[0]
        # Determine the width and height for cropping
        width = min(3840, monitor['width'])
        height = min(1080, monitor['height'])

        # Grab the image
        sct_img = sct.grab({
            "top": monitor["top"], 
            "left": monitor["left"], 
            "width": width, 
            "height": height
        })
        
        screenshot = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)

    # Save the image to a byte array
    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def take_photo():
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()

    # Convert the frame to JPEG format
    _, img_encoded = cv2.imencode('.jpeg', frame)

    # Convert the encoded image array to bytes
    img_byte_arr = img_encoded.tobytes()

    return img_byte_arr

def save_image(image_bytes, filename, format, quality=None):
    """
    Save the image to the specified filename in the specified format.
    
    Parameters:
    - image_bytes: Image data in bytes.
    - filename: Name of the file to save.
    - format: Image format ('JPEG', 'PNG', 'WEBP', etc.).
    - quality: Optional quality parameter for JPEG and WEBP formats.
    """

    img = Image.open(io.BytesIO(image_bytes))
    if format == 'JPEG' and quality:
        img.save(filename, format=format, quality=quality)
    elif format == 'WEBP' and quality:
        img.save(filename, format=format, quality=quality)
    else:
        img.save(filename, format=format)

def reduce_resolution(image_bytes, factor):
    """
    Reduce the resolution of the image by the given factor while maintaining full quality.
    
    Parameters:
    - image_bytes: Image data in bytes.
    - factor: The factor by which to reduce the resolution.
    
    Returns:
    - Bytes of the reduced-resolution image.
    """

    img = Image.open(io.BytesIO(image_bytes))
    # Calculate new dimensions
    new_width = img.width // factor
    new_height = img.height // factor
    # Resize the image
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    # Save the resized image to a byte array
    img_byte_arr = io.BytesIO()
    resized_img.save(img_byte_arr, format='JPEG', quality=100)
    
    return img_byte_arr.getvalue()
# endregion

# Example usage
if __name__ == "__main__":
    # Take a screenshot
    screenshot_bytes = take_screenshot()
    # Save in JPEG format without quality compression
    save_image(screenshot_bytes, "sample/screenshot.jpg", "JPEG")
    # Save in JPEG format with quality compression
    save_image(screenshot_bytes, "sample/screenshot_compressed.jpg", "JPEG", quality=50)
    # Save in WebP format without quality compression
    save_image(screenshot_bytes, "sample/screenshot.webp", "WEBP")
    # Save in WebP format with quality compression
    save_image(screenshot_bytes, "sample/screenshot_compressed.webp", "WEBP", quality=50)
    
    # Take a photo
    photo_bytes = take_photo()
    # Save in JPEG format without quality compression
    save_image(photo_bytes, "sample/photo.jpg", "JPEG")
    # Save in JPEG format with quality compression
    save_image(photo_bytes, "sample/photo_compressed.jpg", "JPEG", quality=50)
    # Save in WebP format without quality compression
    save_image(photo_bytes, "sample/photo.webp", "WEBP")
    # Save in WebP format with quality compression
    save_image(photo_bytes, "sample/photo_compressed.webp", "WEBP", quality=50)

    # Reduce resolution of the screenshot and save
    reduced_screenshot_bytes = reduce_resolution(screenshot_bytes, factor=2)
    save_image(reduced_screenshot_bytes, "sample/reduced_screenshot.jpg", "JPEG")
    # Reduce resolution of the photo and save
    reduced_photo_bytes = reduce_resolution(photo_bytes, factor=2)
    save_image(reduced_photo_bytes, "sample/reduced_photo.jpg", "JPEG")