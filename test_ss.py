import os
import io
import datetime
from mss import mss
from PIL import Image

def take_screenshot_1():
    screenshots = []
    with mss() as sct:
        for monitor_number, monitor in enumerate(sct.monitors[1:], start=1):  # Skip the first entry which is the entire screen
            print(f"Capturing screen: Monitor {monitor_number} at resolution {monitor['width']}x{monitor['height']}")
            sct_img = sct.grab(monitor)
            screenshot = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
            screenshots.append(screenshot)

    if len(screenshots) >= 2:
        first_screenshot = screenshots[0]
        first_width, first_height = first_screenshot.size

        second_screenshot = screenshots[1]
        resized_second_screenshot = second_screenshot.resize((first_width, first_height), Image.Resampling.LANCZOS)

        stitched_image = Image.new('RGB', (first_width * 2, first_height))
        stitched_image.paste(first_screenshot, (0, 0))
        stitched_image.paste(resized_second_screenshot, (first_width, 0))

        img_byte_arr = io.BytesIO()
        stitched_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    else:
        img_byte_arr = io.BytesIO()
        screenshots[0].save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
def take_screenshot_2():
    with mss() as sct:
        # The first entry of sct.monitors is the entire screen
        monitor = sct.monitors[0]
        print(f"Capturing the full screen at resolution {monitor['width']}x{monitor['height']}")
        sct_img = sct.grab(monitor)
        screenshot = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)

    img_byte_arr = io.BytesIO()
    screenshot.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()
def take_screenshot_3():
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

if __name__ == "__main__":
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"screenshot_{timestamp}.jpg"
    save_path = os.path.join("data", filename)
    byte_data = take_screenshot_3()
    with open(save_path, "wb") as f:
        f.write(byte_data)