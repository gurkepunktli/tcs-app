# Frontend ↔ Backend Verbindung

## Übersicht

```
[Handy/Browser] → [Cloudflare Pages PWA] → [Cloudflare Tunnel] → [Docker Backend]
                        Frontend                                       API:8000
```

## Setup

### 1. Lokales Development

**Frontend:**
```bash
cd frontend
cp .env.example .env
# .env bleibt: VITE_API_URL=http://localhost:8000
npm run dev
```

**Backend:**
```bash
cd backend
docker-compose up
```

Frontend läuft auf `http://localhost:5173`
Backend läuft auf `http://localhost:8000`

---

### 2. Production Setup

#### Option A: Cloudflare Tunnel (Empfohlen)

**Schritt 1: Cloudflare Tunnel erstellen**

Siehe [`CLOUDFLARED_PORTAINER.md`](CLOUDFLARED_PORTAINER.md)

1. Container erstellen:
   - Name: `cloudflared-tunnel`
   - Image: `cloudflare/cloudflared:latest`
   - Command: `tunnel run`
   - Env: `TUNNEL_TOKEN=dein_token`
   - Network: `fiber.x_net`

2. Public Hostname konfigurieren:
   - Subdomain: `tcs-api`
   - Domain: `deine-domain.com`
   - Service: `http://tcs-ocr-api:8000`

**Schritt 2: Frontend Environment Variable setzen**

In Cloudflare Pages:
1. Dashboard → Pages → tcs-benzinpreis-frontend
2. Settings → Environment variables
3. Production:
   - `VITE_API_URL` = `https://tcs-api.deine-domain.com`

**Schritt 3: Frontend neu deployen**
```bash
cd frontend
npm run deploy
```

---

#### Option B: Öffentliche IP mit HTTPS

Falls du eine öffentliche IP hast:

1. **Reverse Proxy (nginx/Caddy)**
2. **SSL Zertifikat** (Let's Encrypt)
3. **Cloudflare Pages Env Var:**
   - `VITE_API_URL` = `https://deine-ip-oder-domain.com`

---

## CORS Configuration

Das Backend ist bereits für CORS konfiguriert:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Production: Liste spezifischer Domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Für Production solltest du `allow_origins` einschränken:**

```python
allow_origins=[
    "https://tcs-benzinpreis.pages.dev",
    "https://deine-custom-domain.com"
],
```

---

## Test der Verbindung

### Lokal testen

```bash
# Backend health check
curl http://localhost:8000/health

# OCR Test
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "image=@test.jpg" \
  -F "latitude=47.3769" \
  -F "longitude=8.5417"
```

### Production testen

```bash
# Via Cloudflare Tunnel
curl https://tcs-api.deine-domain.com/health

# OCR Test
curl -X POST "https://tcs-api.deine-domain.com/api/ocr/process" \
  -F "image=@test.jpg" \
  -F "latitude=47.3769" \
  -F "longitude=8.5417"
```

### Frontend testen

1. Öffne PWA im Browser
2. DevTools → Network Tab
3. Foto aufnehmen
4. Upload klicken
5. Prüfe Request zu `${API_URL}/api/ocr/process`

---

## Netzwerk-Architektur

### Lokales Development
```
localhost:5173 (Frontend)
      ↓
localhost:8000 (Backend API)
```

### Production
```
Cloudflare Pages (PWA)
      ↓
https://tcs-api.deine-domain.com (Cloudflare Tunnel)
      ↓
Cloudflare Tunnel Container
      ↓
Docker Network: fiber.x_net
      ↓
tcs-ocr-api:8000 (Backend Container)
```

---

## Troubleshooting

### Frontend kann Backend nicht erreichen

**Lokal:**
- Backend läuft? `docker ps | grep tcs-ocr-api`
- Port 8000 offen? `curl http://localhost:8000/health`
- `.env` korrekt? `cat frontend/.env`

**Production:**
- Cloudflare Tunnel läuft? `docker logs cloudflared-tunnel`
- DNS richtig konfiguriert?
- HTTPS aktiviert?

### CORS Fehler

Browser Konsole zeigt:
```
Access to fetch at 'http://...' from origin 'https://...' has been blocked by CORS policy
```

**Fix:**
1. Backend `main.py` → `allow_origins` anpassen
2. Container neu starten

### Network Error

```
TypeError: Failed to fetch
```

**Mögliche Ursachen:**
1. Backend offline
2. Falsche URL in `VITE_API_URL`
3. Firewall blockiert
4. Mixed content (HTTPS Frontend → HTTP Backend)

**Lösung für Mixed Content:**
- Frontend HTTPS braucht Backend HTTPS
- Nutze Cloudflare Tunnel für automatisches HTTPS

---

## Environment Variables Übersicht

### Frontend

| Variable | Lokal | Production |
|----------|-------|------------|
| `VITE_API_URL` | `http://localhost:8000` | `https://tcs-api.deine-domain.com` |

### Backend

| Variable | Beispiel |
|----------|----------|
| `TCS_COOKIES` | `{"session": "..."}` |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` |
| `LLM_MODEL` | `anthropic/claude-3.5-sonnet` |
| `HEADLESS` | `true` |

---

## Deployment Checklist

- [ ] Backend läuft in Portainer
- [ ] Cloudflare Tunnel konfiguriert
- [ ] Public Hostname zeigt auf Backend
- [ ] Frontend Environment Variable gesetzt
- [ ] Frontend neu deployed
- [ ] Health Check erfolgreich
- [ ] OCR Test erfolgreich
- [ ] Browser DevTools zeigt erfolgreiche Requests
