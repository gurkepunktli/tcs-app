from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io
import re
import os
import json
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
from models import OCRResponse, PriceData
from tcs_submitter import submit_to_tcs

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

        # Perform OCR
        text = pytesseract.image_to_string(img, lang='deu+fra+ita')

        # Extract prices
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


def extract_prices(text: str) -> List[PriceData]:
    """
    Extract fuel prices from OCR text.
    Searches for patterns like:
    - Benzin 95: 1.75
    - Diesel 1.85
    - 95 1.75
    - etc.
    """
    prices = []

    # Normalize text
    text = text.replace(',', '.')

    # Price patterns
    patterns = [
        # "Benzin 95: 1.75" or "Benzin 95 1.75"
        (r'benzin\s*95\D*?(\d+\.\d+)', 'Benzin 95'),
        (r'95\D*?(\d+\.\d+)', 'Benzin 95'),

        # "Benzin 98: 1.85" or "Benzin 98 1.85"
        (r'benzin\s*98\D*?(\d+\.\d+)', 'Benzin 98'),
        (r'98\D*?(\d+\.\d+)', 'Benzin 98'),

        # "Diesel: 1.80" or "Diesel 1.80"
        (r'diesel\D*?(\d+\.\d+)', 'Diesel'),

        # Generic "Super" patterns
        (r'super\s*95\D*?(\d+\.\d+)', 'Benzin 95'),
        (r'super\s*98\D*?(\d+\.\d+)', 'Benzin 98'),
    ]

    text_lower = text.lower()
    seen_types = set()

    for pattern, fuel_type in patterns:
        matches = re.findall(pattern, text_lower)
        if matches and fuel_type not in seen_types:
            try:
                price_value = float(matches[0])
                # Validate reasonable price range (CHF 1.00 - 3.00)
                if 1.0 <= price_value <= 3.0:
                    prices.append(PriceData(type=fuel_type, value=price_value))
                    seen_types.add(fuel_type)
            except ValueError:
                continue

    return prices




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
