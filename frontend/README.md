# TCS Benzinpreis Frontend

Progressive Web App für das Erfassen von Benzinpreisen via Foto und OCR.

## Features

- Kamera-Integration für Mobile Devices
- GPS-Koordinaten Erfassung
- Foto-Upload an OCR Backend
- PWA (installierbar auf Smartphone)

## Entwicklung

```bash
# Dependencies installieren
npm install

# Dev Server starten (http://localhost:3000)
npm run dev

# Production Build
npm run build
```

## Umgebungsvariablen

Kopiere `.env.example` zu `.env` und passe die Backend-URL an:

```bash
cp .env.example .env
```

## Deployment auf Cloudflare Pages

1. GitHub Repository pushen
2. Cloudflare Pages Dashboard öffnen
3. "Create a project" → GitHub Repository verbinden
4. Build Settings:
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Root directory: `frontend`
5. Environment variables setzen:
   - `VITE_API_URL`: URL deines Backend-Servers

## PWA Installation

Auf dem Smartphone die URL öffnen und "Zum Startbildschirm hinzufügen" wählen.
