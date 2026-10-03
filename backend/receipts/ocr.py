import pytesseract # Import pytesseract for OCR functionality
import re # Import re for regular expression handling
from PIL import Image # Import Pillow for image processing

# Function to scan an image and extract all the text using OCR
def scan_image(image_path):

    # Open the image using Pillow
    image = Image.open(image_path)

    # Use pytesseract to extract text from the image and return the extracted text
    text = pytesseract.image_to_string(image, lang='eng+fra')

    return text

# Now there will be a function for each piece of the receipt

# Function to extract the amount from the text
def extract_amount(text):

    # Use a regular expression to find the amount in the text
    patterns = [
        r"TOTAL\s*:?\s*\$?(\d+[.,]\d{2})",  # Matches "TOTAL: $12.34" or "TOTAL $12.34"
        r"TOTAL\s*:?\s*(\d+[.,]\d{2})",  # Matches "TOTAL: 12.34" or "TOTAL 12.34"
        r"AMOUNT\s*:?\s*\$?(\d+[.,]\d{2})",  # Matches "AMOUNT: $12.34" or "AMOUNT $12.34"
        r"AMOUNT\s*:?\s*(\d+[.,]\d{2})",  # Matches "AMOUNT: 12.34" or "AMOUNT 12.34"
    ]

    for line in text.splitlines():
        if re.search(r"\b(?:SOUS[- ]?TOTAL|SUBTOTAL)\b", line, re.IGNORECASE):
            continue  # Skip lines that contain "SOUS-TOTAL" or "SUBTOTAL"

        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', '.'))

    return None

def extract_card_last4(text):
    # Use a regular expression to find the last 4 digits of the card number in the text
    patterns = [
        r"(?:VISA|MASTERCARD|AMEX|CARD)[^\n]{0,20}(?:\*{2,}|X{2,})\s*(\d{4})",  # Matches "VISA **** 1234" or "MASTERCARD XXXX 5678"
        r"(?:\*{2,}|X{2,})\s*(\d{4})",  # Matches "**** 1234" or "XXXX 5678"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None

def extract_merchant(text):

    lines =  [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return None
    
    for line in lines[:3]:
        if re.search(
            r"total|subtotal|tax|tps|tvq|visa|mastercard|amex|interac", line, re.IGNORECASE):
            continue
        
        if re.fullmatch(r"[\d\s\-/.,]+", line):
            continue
        
        return line

    return None

def parse_receipt_text(text):

    return {
        "merchant": extract_merchant(text),
        "amount": extract_amount(text),
        "card_last4": extract_card_last4(text)
    }