# TCS Benzinpreis Backend

OCR-Service für das Auslesen von Benzinpreisen aus Fotos mit automatischer Submission auf benzin.tcs.ch.

## Features

- FastAPI REST API
- Tesseract OCR (Deutsch, Französisch, Italienisch)
- Automatische Preis-Extraktion
- Chrome Headless (Selenium) für automatisches Login & Submit auf TCS
- Keine Datenspeicherung (stateless)

## Setup

### 1. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```

Dann `.env` bearbeiten und TCS-Zugangsdaten eintragen:

```
TCS_USERNAME=your_email@example.com
TCS_PASSWORD=your_password
```

### 2. Starten (Docker Compose)

```bash
# Docker Container starten
docker-compose up -d

# Logs anschauen
docker-compose logs -f

# Container stoppen
docker-compose down
```

### 3. Deployment via Portainer

1. Portainer öffnen
2. Stack erstellen
3. Repository: `https://github.com/gurkepunktli/tcs-app.git`
4. Stack path: `backend`
5. Environment variables setzen (TCS_USERNAME, TCS_PASSWORD)
6. Deploy

Die API läuft auf [http://localhost:8000](http://localhost:8000)

## API Endpoints

### `GET /`
Health Check

### `GET /health`
Detaillierter Health Status

### `POST /api/ocr/process`
Bild hochladen und OCR ausführen

**Form Data:**
- `image`: Bild-Datei (required)
- `latitude`: GPS Breitengrad (optional)
- `longitude`: GPS Längengrad (optional)
- `accuracy`: GPS Genauigkeit in Metern (optional)
- `auto_submit`: Automatisch auf TCS einreichen (optional, default: false)

**Response:**
```json
{
  "success": true,
  "prices": [
    {"type": "Benzin 95", "value": 1.75},
    {"type": "Diesel", "value": 1.80}
  ],
  "raw_text": "Erkannter Text...",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Entwicklung

```bash
# Lokale Entwicklung ohne Docker
cd app
pip install -r ../requirements.txt
uvicorn main:app --reload
```

## API testen

```bash
# Nur OCR (ohne TCS Submit)
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "image=@test_image.jpg" \
  -F "latitude=47.3769" \
  -F "longitude=8.5417"

# Mit automatischem TCS Submit
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "image=@test_image.jpg" \
  -F "latitude=47.3769" \
  -F "longitude=8.5417" \
  -F "auto_submit=true"
```

## Öffentlich zugänglich machen

Für Cloudflare Pages Frontend:

### Option 1: Cloudflare Tunnel
```bash
cloudflared tunnel --url http://localhost:8000
```

### Option 2: ngrok
```bash
ngrok http 8000
```

Dann die URL im Frontend `.env` als `VITE_API_URL` eintragen.
