FROM python:3.11-slim

# Install system dependencies for Tesseract OCR and Playwright
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-ita \
    libtesseract-dev \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium)
RUN playwright install --with-deps chromium

# Workaround for browser-use chromium path detection issue with Playwright 1.57+
# Creates symlink from chrome-linux64 to chrome-linux for browser-use compatibility
RUN for dir in /root/.cache/ms-playwright/chromium-*/; do \
    if [ -d "${dir}chrome-linux64" ] && [ ! -e "${dir}chrome-linux" ]; then \
        ln -s chrome-linux64 "${dir}chrome-linux"; \
    fi \
done

# Copy application code
COPY app/ .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
