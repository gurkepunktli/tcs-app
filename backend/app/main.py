from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io
import re
import os
import json
import base64
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
from models import OCRResponse, PriceData
from tcs_submitter import submit_to_tcs
import httpx

# Load environment variables
load_dotenv()

app = FastAPI(title="TCS Benzinpreis OCR API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message": "TCS Benzinpreis OCR API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/ocr/process", response_model=OCRResponse)
async def process_image(
    image: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    accuracy: Optional[float] = Form(None),
    auto_submit: Optional[bool] = Form(False)
):
    """
    Process an image with OCR to extract fuel prices.
    Optionally auto-submit to TCS website.
    """
    try:
        # Read and validate image
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))

        # Try PaddleOCR first (best for LED displays, fast and local)
        prices = []
        text = ""

        try:
            prices, text = paddleocr_extract_prices(contents)
            print(f"PaddleOCR extraction successful: {prices}")
        except Exception as paddle_error:
            print(f"PaddleOCR failed: {paddle_error}, falling back to Tesseract")

            # Fallback to Tesseract OCR
            from PIL import ImageEnhance, ImageFilter

            # Strategy 1: Digits-only OCR with aggressive preprocessing
            img_digits = img.convert('L')
            img_digits = img_digits.filter(ImageFilter.SHARPEN)
            enhancer = ImageEnhance.Contrast(img_digits)
            img_digits = enhancer.enhance(3.0)
            enhancer = ImageEnhance.Brightness(img_digits)
            img_digits = enhancer.enhance(1.2)
            digits_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'
            text_digits = pytesseract.image_to_string(img_digits, config=digits_config)

            # Strategy 2: Standard OCR
            img_standard = img.convert('L')
            enhancer = ImageEnhance.Contrast(img_standard)
            img_standard = enhancer.enhance(2.0)
            standard_config = r'--oem 3 --psm 6'
            text_standard = pytesseract.image_to_string(img_standard, lang='deu+fra+ita', config=standard_config)

            text = text_digits if len(text_digits.strip()) > len(text_standard.strip()) else text_standard
            print(f"Tesseract fallback - Selected: {'digits' if text == text_digits else 'standard'}")

            # Extract prices from Tesseract output
            prices = extract_prices(text)

        # Log the result
        print(f"OCR processed - Lat: {latitude}, Lng: {longitude}")
        print(f"Extracted prices: {prices}")

        # Auto-submit to TCS if requested and credentials/cookies are available
        submission_success = False
        if auto_submit and latitude and longitude:
            # Try to load cookies from environment (JSON string)
            tcs_cookies = None
            tcs_cookies_json = os.getenv('TCS_COOKIES')
            if tcs_cookies_json:
                try:
                    tcs_cookies = json.loads(tcs_cookies_json)
                except json.JSONDecodeError:
                    print("Warning: TCS_COOKIES is not valid JSON")

            # Fallback to username/password
            tcs_username = os.getenv('TCS_USERNAME')
            tcs_password = os.getenv('TCS_PASSWORD')

            if tcs_cookies or (tcs_username and tcs_password):
                prices_dict = {
                    'benzin_95': next((p.value for p in prices if 'benzin' in p.type.lower() and '95' in p.type), None),
                    'benzin_98': next((p.value for p in prices if 'benzin' in p.type.lower() and '98' in p.type), None),
                    'diesel': next((p.value for p in prices if 'diesel' in p.type.lower()), None)
                }

                try:
                    # Run async submit_to_tcs function
                    submission_success = await submit_to_tcs(
                        latitude=latitude,
                        longitude=longitude,
                        prices=prices_dict,
                        cookies=tcs_cookies,
                        username=tcs_username,
                        password=tcs_password
                    )
                    print(f"TCS submission: {'Success' if submission_success else 'Failed'}")
                except Exception as submit_error:
                    print(f"TCS submission error: {str(submit_error)}")
            else:
                print("No TCS credentials or cookies available for auto-submit")

        return OCRResponse(
            success=True,
            prices=prices,
            raw_text=text,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# Global PaddleOCR instance (initialized once to avoid reloading models)
_paddle_ocr = None

def get_paddle_ocr():
    """Lazy load PaddleOCR instance (singleton pattern)"""
    global _paddle_ocr
    if _paddle_ocr is None:
        from paddleocr import PaddleOCR
        # Initialize with English model, CPU mode, disable angle classification for speed
        _paddle_ocr = PaddleOCR(
            use_angle_cls=False,
            lang='en',
            show_log=False
        )
    return _paddle_ocr


def paddleocr_extract_prices(image_bytes: bytes) -> tuple[List[PriceData], str]:
    """
    Use PaddleOCR to extract fuel prices from LED displays.
    Returns (prices, raw_text) tuple.
    """
    import numpy as np
    import cv2

    # Load image with OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Get PaddleOCR instance
    ocr = get_paddle_ocr()

    # Perform OCR
    results = ocr.ocr(img, cls=False)

    if not results or not results[0]:
        raise ValueError("PaddleOCR found no text")

    # Extract detected text and bounding boxes
    detected_texts = []
    for line in results[0]:
        bbox, (text, confidence) = line
        # Only keep detections with digits
        if any(c.isdigit() for c in text) and confidence > 0.5:
            detected_texts.append((text, bbox, confidence))
            print(f"PaddleOCR detected: '{text}' (confidence: {confidence:.2f})")

    # Combine all detected text
    raw_text = ' '.join([text for text, _, _ in detected_texts])

    # Filter to only digits and dots
    filtered_texts = []
    for text, bbox, conf in detected_texts:
        # Remove non-digit characters except dots
        cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
        if cleaned:
            filtered_texts.append((cleaned, bbox, conf))

    # Extract price-like patterns
    price_pattern = r'(\d{1,2}\.\d{1,3})'
    prices_with_pos = []

    for text, bbox, conf in filtered_texts:
        for price_str in re.findall(price_pattern, text):
            try:
                price = float(price_str)
                if 1.0 <= price <= 3.0:  # Reasonable CHF price range
                    # Calculate vertical center of bounding box
                    y_coords = [point[1] for point in bbox]
                    y_center = sum(y_coords) / len(y_coords)
                    prices_with_pos.append((price, y_center))
                    print(f"Valid price found: {price} at Y={y_center}")
            except (ValueError, IndexError):
                continue

    # Sort by Y position (top to bottom)
    prices_with_pos.sort(key=lambda x: x[1])
    sorted_prices = [price for price, _ in prices_with_pos]

    # Remove duplicates while preserving order
    seen = set()
    unique_prices = []
    for p in sorted_prices:
        if p not in seen:
            seen.add(p)
            unique_prices.append(p)

    # Map prices based on position
    prices = []
    if len(unique_prices) == 3:
        prices = [
            PriceData(type='Benzin 95', value=unique_prices[0]),
            PriceData(type='Benzin 98', value=unique_prices[1]),
            PriceData(type='Diesel', value=unique_prices[2])
        ]
    elif len(unique_prices) == 2:
        prices = [
            PriceData(type='Benzin 95', value=unique_prices[0]),
            PriceData(type='Diesel', value=unique_prices[1])
        ]
    elif len(unique_prices) == 1:
        prices = [
            PriceData(type='Benzin 95', value=unique_prices[0])
        ]
    else:
        raise ValueError(f"Could not extract valid prices. Found: {unique_prices}")

    return prices, raw_text


def extract_prices(text: str) -> List[PriceData]:
    """
    Extract fuel prices from OCR text using line-based approach.

    Assumes:
    - 3 lines = Line 1: Benzin 95, Line 2: Benzin 98, Line 3: Diesel
    - 2 lines = Line 1: Benzin 95, Line 2: Diesel
    """
    prices = []

    # Normalize text
    text = text.replace(',', '.')

    # Remove whitespace and newlines for cleaner processing
    text_cleaned = ' '.join(text.split())

    # Log OCR text for debugging
    print(f"OCR Text: {text}")
    print(f"Cleaned: {text_cleaned}")

    # Extract all price-like numbers (format: X.XX or X.XXX or just X.X)
    # Matches: 1.72, 1.80, 1.723, 1.86, etc.
    price_pattern = r'(\d{1,2}\.\d{1,3})'
    found_prices = re.findall(price_pattern, text_cleaned)
    print(f"Found prices: {found_prices}")

    # Convert to floats and validate range
    valid_prices = []
    for price_str in found_prices:
        try:
            price = float(price_str)
            if 1.0 <= price <= 3.0:  # Reasonable CHF price range
                valid_prices.append(price)
        except ValueError:
            continue

    # Map prices based on position
    if len(valid_prices) == 3:
        # 3 prices: Benzin 95, Benzin 98, Diesel
        prices = [
            PriceData(type='Benzin 95', value=valid_prices[0]),
            PriceData(type='Benzin 98', value=valid_prices[1]),
            PriceData(type='Diesel', value=valid_prices[2])
        ]
    elif len(valid_prices) == 2:
        # 2 prices: Benzin 95, Diesel
        prices = [
            PriceData(type='Benzin 95', value=valid_prices[0]),
            PriceData(type='Diesel', value=valid_prices[1])
        ]
    elif len(valid_prices) == 1:
        # Only 1 price found, assume Benzin 95
        prices = [
            PriceData(type='Benzin 95', value=valid_prices[0])
        ]

    return prices




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
