import re

try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]')

HINGLISH_KEYWORDS = re.compile(
    r'\b(aaj|kal|jaldi|paisa|paise|fees|bharo|mileyga|kamayein|ghar|baith|kaam|bharti|sarkari|naukri|whatsapp|karo|bhej|de|ho|hai|ko|par|se|mein)\b',
    re.IGNORECASE
)

def detect_language(text):
    """
    Detect language of the posting text:
    Returns dict: {'code': 'en'|'hi'|'hi-Latn', 'label': 'English'|'Hindi (Devanagari)'|'Hinglish'}
    """
    if not isinstance(text, str) or not text.strip():
        return {'code': 'en', 'label': 'English'}
        
    devanagari_chars = len(DEVANAGARI_REGEX.findall(text))
    total_chars = max(1, len(text.replace(" ", "")))
    
    # If substantial Devanagari script present
    if devanagari_chars / total_chars > 0.05 or devanagari_chars > 10:
        return {'code': 'hi', 'label': 'Hindi (Devanagari)'}
        
    # Check for Hinglish (Latin script code-mixed Hindi)
    hinglish_matches = len(HINGLISH_KEYWORDS.findall(text))
    if hinglish_matches >= 3:
        return {'code': 'hi-Latn', 'label': 'Hinglish'}
        
    # Use langdetect library fallback if available
    if LANGDETECT_AVAILABLE:
        try:
            detected = detect(text)
            if detected == 'hi':
                return {'code': 'hi', 'label': 'Hindi (Devanagari)'}
        except Exception:
            pass
            
    return {'code': 'en', 'label': 'English'}
