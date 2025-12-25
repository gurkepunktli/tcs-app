# TCS Benzinpreis OCR App

Eine Progressive Web App zum Erfassen von Benzinpreisen via Foto und OCR-Erkennung mit automatischer Übermittlung an benzin.tcs.ch.

## Architektur

```
tcs-app/
├── frontend/          # Cloudflare Pages (PWA)
├── backend/           # Docker Container (OCR API + AI Browser Automation)
└── docs/              # Dokumentation
```

## Features

- 📷 Foto von Benzinpreis-Tafeln aufnehmen (Mobile Camera)
- 🔍 Automatische OCR-Erkennung der Preise (Tesseract OCR)
- 📍 GPS-Koordinaten erfassen
- 🤖 AI-gesteuerte Browser-Automatisierung (browser-use)
- 🚀 Automatische Übermittlung an benzin.tcs.ch
- 🍪 Cookie-basierte Authentifizierung

## Tech Stack

### Frontend (Cloudflare Pages)
- HTML5/CSS3/JavaScript
- Camera API & Geolocation API
- Progressive Web App (PWA)
- Vite Build System

### Backend (Docker)
- FastAPI (Python)
- Tesseract OCR (deu/fra/ita)
- browser-use (AI-gesteuerte Browser-Automatisierung)
- Playwright (Headless Browser)
- OpenRouter API (LLM für AI Agent)
- Docker Compose

## Deployment

### Frontend
```bash
cd frontend
npm install
npm run build
# Deploy via Cloudflare Pages (auto-deploy from GitHub)
```

### Backend (Docker via Portainer)

1. **Erstelle `.env` Datei** basierend auf `.env.example`:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Konfiguriere Umgebungsvariablen** in `.env`:
   - `TCS_COOKIES`: Cookies von benzin.tcs.ch (siehe `backend/COOKIE_HOWTO.md`)
   - `OPENROUTER_API_KEY`: API Key von https://openrouter.ai/
   - `LLM_MODEL`: z.B. `anthropic/claude-3.5-sonnet` (empfohlen)
   - `HEADLESS`: `true` für Produktiv, `false` für Debugging

3. **Docker Container starten**:
   ```bash
   cd backend
   docker-compose up -d
   ```

4. **Via Portainer** (siehe [`PORTAINER_SETUP.md`](PORTAINER_SETUP.md)):
   - Stack importieren aus GitHub
   - Network: `fiber.x_net` (external)
   - Environment Variables setzen

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

## Konfiguration

### 1. TCS Cookies exportieren

Siehe ausführliche Anleitung in [`backend/COOKIE_HOWTO.md`](backend/COOKIE_HOWTO.md)

**Kurzanleitung:**
1. Auf https://benzin.tcs.ch einloggen
2. Browser DevTools öffnen (F12)
3. Application/Storage → Cookies
4. Session/Auth Cookies kopieren
5. Als JSON in `.env` eintragen:
   ```bash
   TCS_COOKIES={"session": "abc123...", "auth_token": "xyz789..."}
   ```

### 2. OpenRouter API Key

1. Account erstellen auf https://openrouter.ai/
2. API Key generieren
3. In `.env` eintragen:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

### 3. LLM Modell wählen

Empfohlene Modelle:
- `anthropic/claude-3.5-sonnet` - Beste Balance (empfohlen, ~$0.01/submission)
- `anthropic/claude-3-haiku` - Schneller & günstiger (~$0.002/submission)
- `openai/gpt-4o` - Alternative (~$0.015/submission)

## API Verwendung

### OCR Endpunkt

```bash
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "image=@photo.jpg" \
  -F "latitude=47.3769" \
  -F "longitude=8.5417" \
  -F "auto_submit=true"
```

**Parameter:**
- `image`: Foto-Datei (jpg/png)
- `latitude`: GPS Breitengrad
- `longitude`: GPS Längengrad
- `accuracy`: GPS Genauigkeit (optional)
- `auto_submit`: `true` für automatische TCS-Übermittlung

**Response:**
```json
{
  "success": true,
  "prices": [
    {"type": "Benzin 95", "value": 1.75},
    {"type": "Diesel", "value": 1.80}
  ],
  "raw_text": "...",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Wie es funktioniert

1. **Foto aufnehmen**: PWA nutzt Camera API auf dem Handy
2. **GPS erfassen**: Geolocation API liest aktuelle Koordinaten
3. **Upload**: Foto + GPS werden an Backend API gesendet
4. **OCR-Extraktion**: Tesseract erkennt Benzinpreise aus dem Foto
5. **AI Browser Automation**:
   - browser-use Agent startet Playwright Browser
   - GPS-Koordinaten werden im Browser gesetzt
   - AI findet die nächste Tankstelle auf der Karte
   - AI klickt auf "AKTUALISIEREN" Buttons
   - AI trägt die neuen Preise ein
6. **TCS Submission**: Preise werden auf benzin.tcs.ch übermittelt

## Kosten

**OpenRouter API Kosten** (ca. pro Submission):
- Claude 3.5 Sonnet: $0.005 - $0.015
- Claude 3 Haiku: $0.001 - $0.003
- GPT-4o: $0.010 - $0.020

Die Kosten variieren je nach Komplexität der Webseite.

## Troubleshooting

### Cookies funktionieren nicht
- Prüfe, ob Cookies noch gültig sind (können ablaufen)
- Exportiere neue Cookies nach erneutem Login

### AI Agent findet Tankstelle nicht
- Prüfe GPS-Koordinaten (müssen nahe bei einer Tankstelle sein)
- Teste mit `HEADLESS=false` um Browser zu sehen
- Logs prüfen: `docker logs tcs-ocr-api`

### Playwright Installation fehlgeschlagen
```bash
docker-compose build --no-cache
```

## Dokumentation

- [`PORTAINER_SETUP.md`](PORTAINER_SETUP.md) - Portainer Deployment Guide
- [`backend/COOKIE_HOWTO.md`](backend/COOKIE_HOWTO.md) - Cookies exportieren
- [`backend/NEXT_STEPS.md`](backend/NEXT_STEPS.md) - Entwicklungs-Guide
- [browser-use Docs](https://github.com/browser-use/browser-use)

## Lizenz

MIT
