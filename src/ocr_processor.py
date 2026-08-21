import os
import cv2
import numpy as np
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
    
    # Auto-detect Tesseract executable on Windows if not already in PATH
    POSSIBLE_PATHS = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    ]
    for pth in POSSIBLE_PATHS:
        if os.path.exists(pth):
            pytesseract.pytesseract.tesseract_cmd = pth
            break
except ImportError:
    TESSERACT_AVAILABLE = False

def preprocess_image(image_bytes_or_path):
    """
    Preprocess image for optimal Tesseract OCR accuracy on screenshots.
    Converts to grayscale, applies noise reduction and adaptive/Otsu thresholding.
    """
    if isinstance(image_bytes_or_path, str):
        img = cv2.imread(image_bytes_or_path)
    else:
        nparr = np.frombuffer(image_bytes_or_path, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
    if img is None:
        raise ValueError("Could not decode image file.")
        
    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Resize if too small
    height, width = gray.shape[:2]
    if width < 800:
        scale = 800.0 / width
        gray = cv2.resize(gray, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_CUBIC)
        
    # Denoise & Thresholding
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return gray, thresh

def extract_text_from_image(image_bytes_or_path):
    """
    Extract text using pytesseract with fallback error handling.
    Returns (extracted_text, success, error_message)
    """
    if not TESSERACT_AVAILABLE:
        return "", False, "Pytesseract or PIL library is not installed in the Python environment."
        
    try:
        gray, thresh = preprocess_image(image_bytes_or_path)
        
        # Try OCR on thresholded image first
        pil_img = Image.fromarray(thresh)
        text = pytesseract.image_to_string(pil_img, lang='eng+hin')
        
        if not text or len(text.strip()) < 5:
            # Fallback to grayscale OCR
            pil_img_gray = Image.fromarray(gray)
            text = pytesseract.image_to_string(pil_img_gray)
            
        cleaned_text = text.strip()
        if not cleaned_text:
            return "", False, "No readable text detected in the uploaded image. Please ensure the image is clear."
            
        return cleaned_text, True, None
    except Exception as e:
        err_msg = str(e)
        if "tesseract is not installed" in err_msg.lower() or "tesseract-ocr" in err_msg.lower() or "not in your path" in err_msg.lower():
            return "", False, "Tesseract OCR engine is not installed on system PATH. Please install Tesseract-OCR."
        return "", False, f"OCR Processing Error: {err_msg}"
