# TCS Benzinpreis OCR App

Eine Progressive Web App zum Erfassen von Benzinpreisen via Foto und OCR-Erkennung.

## Architektur

```
tcs-app/
├── frontend/          # Cloudflare Pages (PWA)
├── backend/           # Docker Container (OCR API)
└── docs/              # Dokumentation
```

## Features

- Foto von Benzinpreis-Tafeln aufnehmen (Mobile Camera)
- Automatische OCR-Erkennung der Preise
- GPS-Koordinaten erfassen
- Preise in Datenbank speichern
- Historie und Kartenansicht

## Tech Stack

### Frontend (Cloudflare Pages)
- HTML5/CSS3/TypeScript
- Camera API & Geolocation API
- Progressive Web App (PWA)

### Backend (Docker)
- FastAPI (Python)
- Tesseract OCR / EasyOCR
- PostgreSQL + PostGIS
- Docker Compose

## Deployment

### Frontend
```bash
cd frontend
npm install
npm run build
# Deploy via Cloudflare Pages (auto-deploy from GitHub)
```

### Backend
```bash
cd backend
docker-compose up -d
```

## Entwicklung

### Frontend lokal starten
```bash
cd frontend
npm install
npm run dev
```

### Backend lokal starten
```bash
cd backend
docker-compose up
```

## Umgebungsvariablen

Siehe `.env.example` Dateien in den jeweiligen Ordnern.

## Lizenz

MIT
