# Architektur-Dokumentation

## Übersicht

Die TCS Benzinpreis OCR App besteht aus zwei Hauptkomponenten:

```
Frontend (Cloudflare Pages) ←→ Backend (Docker/Lokal)
```

## Frontend

**Deployment:** Cloudflare Pages (automatisch via GitHub)
**Technologie:** Vanilla JavaScript + Vite
**Features:**
- Progressive Web App (PWA)
- Kamera-Integration (Mobile)
- GPS-Koordinaten
- Offline-Fähigkeit (Service Worker)

**Ordner:** `/frontend`

## Backend

**Deployment:** Lokaler Docker Container
**Technologie:** Python FastAPI + Tesseract OCR
**Features:**
- OCR-Verarbeitung (Deutsch, Französisch, Italienisch)
- Preis-Extraktion via Regex
- Stateless (keine Datenspeicherung)

**Ordner:** `/backend`

## Datenfluss

1. User öffnet PWA auf Smartphone
2. User macht Foto von Benzinpreis-Tafel
3. GPS-Koordinaten werden erfasst
4. Foto + Koordinaten → Backend API
5. Backend: OCR-Verarbeitung
6. Backend: Preis-Extraktion via Pattern Matching
7. Ergebnis → Frontend
8. Anzeige der erkannten Preise

## Deployment-Strategie

### Frontend
- GitHub Push → Automatisches Cloudflare Pages Deployment
- Build: `npm run build`
- Output: `/frontend/dist`

### Backend
- Lokaler Docker Container
- Zugriff via Cloudflare Tunnel oder ngrok
- Keine persistente Datenspeicherung

## Skalierung

Falls später Datenspeicherung gewünscht:
- PostgreSQL + PostGIS für Geo-Daten
- Siehe Git-History für ursprüngliches DB-Setup

## Sicherheit

- CORS aktiviert für Frontend-Zugriff
- HTTPS via Cloudflare
- Kein Login erforderlich (public API)
