import os
import easyocr
import subprocess
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Path to the Tesseract executable, update this if Tesseract is installed in a different location
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def negate_image(image_path, output_path):
    try:
        with Image.open(image_path) as img:
            # Convert image to grayscale
            grayscale_img = img.convert('L')
            # Invert the grayscale image
            inverted_img = Image.eval(grayscale_img, lambda x: 255 - x)
            # Save the inverted image
            inverted_img.save(output_path)
        return True
    except Exception as e:
        print("Error:", e)
        return False

def extract_text_from_image_tesseract(image_path):
    try:
        with Image.open(image_path) as img:
            extracted_text = pytesseract.image_to_string(img)
            return extracted_text
    except Exception as e:
        print("Error:", e)
        return None

def extract_text_from_image_easyocr(image_path):
    try:
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_path)
        extracted_text = ' '.join([text[1] for text in result])
        return extracted_text
    except Exception as e:
        print("Error:", e)
        return None

# Input and output image paths
input_image_path = 'sample/screenshot_compressed.jpg'
output_image_path = 'sample/negated_screenshot.jpg'

# Negate the image
if negate_image(input_image_path, output_image_path):
    print("Image negation successful.")
else:
    print("Image negation failed.")

# Perform OCR using both Tesseract and EasyOCR in parallel
with ThreadPoolExecutor() as executor:
    future_tesseract = executor.submit(extract_text_from_image_tesseract, output_image_path)
    # future_easyocr = executor.submit(extract_text_from_image_easyocr, output_image_path)

# Get OCR results
extracted_text_tesseract = future_tesseract.result()
print(f"Extracted Text (Tesseract)\n{extracted_text_tesseract}")
# extracted_text_easyocr = future_easyocr.result()
# print(f"Extracted Text (EasyOCR)\n{extracted_text_easyocr}")