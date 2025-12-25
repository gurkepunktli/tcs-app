# Nächste Schritte zur Vervollständigung

## 🔍 Schritt 1: benzin.tcs.ch analysieren

Du musst die tatsächliche Webseite untersuchen, um die korrekten Selektoren zu finden.

### Option A: Browser DevTools (Empfohlen)
1. Öffne https://benzin.tcs.ch im Chrome/Firefox
2. F12 → **Network** Tab öffnen
3. Versuche:
   - Dich einzuloggen
   - Einen Preis zu melden
4. Schau dir die Requests an:
   - Welche API-Endpoints? (z.B. `POST /api/auth/login`, `POST /api/prices`)
   - Welche Request-Bodies?
   - Gibt es einen Bearer Token / Session Cookie?

### Option B: Selenium-Analyse-Script
```bash
cd backend/app
python analyze_tcs.py --no-headless
```

Dies öffnet einen Browser und zeigt dir:
- Alle Buttons, Links, Input-Felder
- Login-Elemente
- Preis-Submit-Elemente
- Screenshot + HTML-Dump

## 📝 Schritt 2: Selektoren in Code einfügen

Basierend auf deiner Analyse, fülle die TODOs in `backend/app/tcs_submitter.py` aus:

### Login implementieren (Zeile 56-97)
```python
# Beispiel - ersetze mit echten Selektoren:
login_btn = self.driver.find_element(By.CSS_SELECTOR, '.login-button')
login_btn.click()

email_field = WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.ID, "email"))
)
email_field.send_keys(self.username)

password_field = self.driver.find_element(By.ID, "password")
password_field.send_keys(self.password)

submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
submit_btn.click()
```

### Preis-Submit implementieren (Zeile 135-180)
```python
# Beispiel - ersetze mit echten Selektoren:
add_price_btn = WebDriverWait(self.driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="add-price"]'))
)
add_price_btn.click()

# Tankstelle auswählen (evtl. basierend auf GPS)
station_select = self.driver.find_element(By.CSS_SELECTOR, '.station-list li:first-child')
station_select.click()

# Preise eingeben
if benzin_95:
    benzin95_input = self.driver.find_element(By.NAME, 'benzin95')
    benzin95_input.send_keys(str(benzin_95))

submit = self.driver.find_element(By.CSS_SELECTOR, 'button.submit-prices')
submit.click()
```

## 🔧 Schritt 3: Testen

### Lokal testen (ohne Docker):
```bash
cd backend/app
pip install -r ../requirements.txt

# Teste das Analyse-Script
python analyze_tcs.py --no-headless

# Teste die API
uvicorn main:app --reload
```

### Mit Docker testen:
```bash
cd backend
docker-compose up --build
```

### Test Request:
```bash
curl -X POST "http://localhost:8000/api/ocr/process" \
  -F "image=@test_image.jpg" \
  -F "latitude=47.3769" \
  -F "longitude=8.5417" \
  -F "auto_submit=true"
```

## 🚀 Schritt 4: Deployment

1. **Push die Änderungen:**
   ```bash
   git add .
   git commit -m "Implement TCS selectors"
   git push
   ```

2. **Portainer:**
   - Stack aktualisieren
   - Environment Variables setzen (TCS_USERNAME, TCS_PASSWORD)

3. **Cloudflare Pages:**
   - Frontend wird automatisch deployed

## 📚 Wichtige Hinweise

### GPS-Koordinaten
- ✅ Werden jetzt via `execute_cdp_cmd` im Browser gesetzt
- ✅ benzin.tcs.ch sieht die "gefälschten" Koordinaten als echt
- ✅ Du kannst von überall Preise für beliebige Tankstellen melden

### Alternative: API statt Selenium
Falls benzin.tcs.ch eine öffentliche API hat:
- Finde die API-Endpoints via Browser DevTools
- Ersetze Selenium mit direkten HTTP-Requests
- Schneller & resourceneffizienter

## ❓ Fragen?

1. **Gibt es einen TCS API-Dokumentation?**
   - Schau in den Network-Requests nach
   - Evtl. ist alles über REST-API lösbar

2. **Braucht man wirklich Login?**
   - Oder kann man anonym Preise melden?
   - Prüfe das in der Webapp

3. **Wie wählt man die Tankstelle aus?**
   - Wird sie automatisch via GPS erkannt?
   - Muss man sie aus einer Liste wählen?
   - Gibt es eine Station-ID?
