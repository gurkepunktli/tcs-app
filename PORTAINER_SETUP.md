# Portainer Deployment Guide

## Methode 1: Git Repository Stack (Empfohlen)

### Schritt 1: Stack erstellen
1. Portainer öffnen
2. **Stacks** → **Add stack**
3. Name: `tcs-benzinpreis`
4. Build method: **Repository**

### Schritt 2: Repository konfigurieren
- **Repository URL**: `https://github.com/gurkepunktli/tcs-app`
- **Repository reference**: `refs/heads/main`
- **Compose path**: `docker-compose.yml`

### Schritt 3: Environment Variables setzen

Klicke auf **Add an environment variable** und füge folgende Variablen hinzu:

**Pflichtfelder:**
```
TCS_COOKIES={"session": "dein_session_cookie", "auth_token": "dein_auth_token"}
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
```

**Optional (mit Defaults):**
```
LLM_MODEL=anthropic/claude-3.5-sonnet
HEADLESS=true
API_HOST=0.0.0.0
API_PORT=8000
```

### Schritt 4: Deploy
- Klicke **Deploy the stack**
- Warte, bis der Build abgeschlossen ist
- Container sollte starten

---

## Methode 2: Custom Template (Alternative)

### Schritt 1: Template erstellen
1. Portainer → **App Templates** → **Custom Templates**
2. **Add Custom Template**
3. Title: `TCS Benzinpreis API`
4. Description: `OCR API mit browser-use Automation`

### Schritt 2: Template Content
Kopiere den Inhalt von `portainer-stack.yml`:

```yaml
version: '3.8'

services:
  tcs-api:
    image: tcs-ocr-api:latest
    build:
      context: https://github.com/gurkepunktli/tcs-app.git#main
      dockerfile: backend/Dockerfile
    container_name: tcs-ocr-api
    ports:
      - "8000:8000"
    environment:
      - TCS_COOKIES=${TCS_COOKIES}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LLM_MODEL=${LLM_MODEL:-anthropic/claude-3.5-sonnet}
      - HEADLESS=${HEADLESS:-true}
    networks:
      - fiber.x_net
    restart: unless-stopped

networks:
  fiber.x_net:
    external: true
```

### Schritt 3: Variables definieren
Füge folgende Variables hinzu:

| Name | Label | Default | Description |
|------|-------|---------|-------------|
| `TCS_COOKIES` | TCS Cookies (JSON) | | Required: Session cookies from benzin.tcs.ch |
| `OPENROUTER_API_KEY` | OpenRouter API Key | | Required: API key from openrouter.ai |
| `LLM_MODEL` | LLM Model | `anthropic/claude-3.5-sonnet` | Optional: AI model choice |
| `HEADLESS` | Headless Mode | `true` | Optional: Run browser headless |

### Schritt 4: Stack aus Template deployen
1. **App Templates** → Wähle dein Template
2. Name: `tcs-benzinpreis`
3. Fülle Environment Variables aus
4. Deploy

---

## Methode 3: Web Editor (Schnellste)

### Schritt 1: Stack erstellen
1. Portainer → **Stacks** → **Add stack**
2. Name: `tcs-benzinpreis`
3. Build method: **Web editor**

### Schritt 2: Compose File einfügen
Kopiere folgenden Code in den Editor:

```yaml
version: '3.8'

services:
  tcs-api:
    build:
      context: https://github.com/gurkepunktli/tcs-app.git#main
      dockerfile: backend/Dockerfile
    container_name: tcs-ocr-api
    ports:
      - "8000:8000"
    environment:
      - TCS_COOKIES={"session": "DEIN_SESSION_COOKIE"}
      - OPENROUTER_API_KEY=sk-or-v1-DEIN_API_KEY
      - LLM_MODEL=anthropic/claude-3.5-sonnet
      - HEADLESS=true
    networks:
      - fiber.x_net
    restart: unless-stopped

networks:
  fiber.x_net:
    external: true
```

### Schritt 3: Ersetze Placeholders
- `DEIN_SESSION_COOKIE` → Echte Cookies von benzin.tcs.ch
- `DEIN_API_KEY` → OpenRouter API Key

### Schritt 4: Deploy
- Klicke **Deploy the stack**

---

## Nach dem Deployment

### Container überprüfen
```bash
docker logs tcs-ocr-api
```

### API testen
```bash
curl http://localhost:8000/health
```

Erwartete Antwort:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

### API verwenden
```bash
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "image=@photo.jpg" \
  -F "latitude=47.3769" \
  -F "longitude=8.5417" \
  -F "auto_submit=true"
```

---

## Troubleshooting

### Build schlägt fehl
```bash
# In Portainer:
# Stack → tcs-benzinpreis → Editor
# Ändere `build:` zu `image:` wenn du ein vorgefertigtes Image hast

# Oder baue lokal und pushe zu Docker Hub:
cd backend
docker build -t your-dockerhub-username/tcs-ocr-api:latest .
docker push your-dockerhub-username/tcs-ocr-api:latest

# Dann in Portainer:
image: your-dockerhub-username/tcs-ocr-api:latest
```

### Network "fiber.x_net" existiert nicht
```bash
# Erstelle das Network manuell:
docker network create fiber.x_net

# Oder in Portainer:
# Networks → Add network
# Name: fiber.x_net
```

### Container startet nicht
```bash
# Logs prüfen:
docker logs tcs-ocr-api

# Häufige Probleme:
# - OPENROUTER_API_KEY fehlt
# - TCS_COOKIES ungültiges JSON
# - Playwright Installation fehlgeschlagen
```

### Playwright Installation dauert lange
Das ist normal! Der erste Build kann 5-10 Minuten dauern, weil Playwright Chromium herunterladen muss.

---

## Environment Variables - Vollständige Referenz

| Variable | Pflicht | Default | Beschreibung |
|----------|---------|---------|--------------|
| `TCS_COOKIES` | Ja | - | JSON mit Session-Cookies von benzin.tcs.ch |
| `OPENROUTER_API_KEY` | Ja | - | API Key von https://openrouter.ai/ |
| `LLM_MODEL` | Nein | `anthropic/claude-3.5-sonnet` | LLM Modell für browser-use |
| `HEADLESS` | Nein | `true` | Browser im Headless-Modus |
| `API_HOST` | Nein | `0.0.0.0` | API Bind-Adresse |
| `API_PORT` | Nein | `8000` | API Port |
| `TCS_USERNAME` | Nein | - | Fallback: TCS Username (wenn keine Cookies) |
| `TCS_PASSWORD` | Nein | - | Fallback: TCS Passwort (wenn keine Cookies) |

---

## Updates deployen

### Auto-Update (bei Git Repository Stack):
1. Stack öffnen
2. **Pull and redeploy** Button klicken
3. Wartet auf neuen GitHub Commit

### Manuelles Update:
```bash
# Lokaler Rebuild:
docker-compose build --no-cache
docker-compose up -d
```

---

## Monitoring

### Container Status
```bash
docker ps | grep tcs-ocr-api
```

### Ressourcen-Nutzung
```bash
docker stats tcs-ocr-api
```

### Live Logs
```bash
docker logs -f tcs-ocr-api
```
