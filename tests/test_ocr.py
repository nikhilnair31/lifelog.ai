import easyocr
import pytesseract
from PIL import Image

# Path to the Tesseract executable, update this if Tesseract is installed in a different location
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

image_path = 'sample/reduced_photo.jpg'

extracted_text_tesseract = extract_text_from_image_tesseract(image_path)
extracted_texr_easyocr = extract_text_from_image_easyocr(image_path)

print(f"Extracted Tesseract Text: {extracted_text_tesseract}")
print(f"Extracted EasyOCR Text: {extracted_texr_easyocr}")