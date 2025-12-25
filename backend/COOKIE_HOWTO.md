# Cookies aus dem Browser exportieren

## Schritt 1: Im Browser einloggen

1. Öffne https://benzin.tcs.ch
2. Logge dich mit deinem TCS-Account ein
3. Stelle sicher, dass du eingeloggt bist (erkennst du am Profil-Icon)

## Schritt 2: Cookies finden

### Chrome/Edge:
1. **F12** drücken (DevTools öffnen)
2. Tab **Application** öffnen
3. Links im Menü: **Storage** → **Cookies** → `https://benzin.tcs.ch`
4. Rechts siehst du alle Cookies

### Firefox:
1. **F12** drücken
2. Tab **Storage** öffnen
3. Links: **Cookies** → `https://benzin.tcs.ch`

## Schritt 3: Relevante Cookies identifizieren

Suche nach Cookies mit Namen wie:
- `session`
- `auth`
- `token`
- `user`
- `tcs_*`
- oder ähnlich

**Beispiel Screenshot:**
```
Name           | Value
---------------|----------------------------------
session        | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
auth_token     | 8f3a9c2b1d4e6f7g8h9i0j1k2l3m4n5o6p
csrf_token     | a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r
```

## Schritt 4: Cookies kopieren

Klicke auf ein Cookie → Kopiere den **Value**

## Schritt 5: In .env eintragen

Erstelle eine `.env` Datei im `backend/` Ordner:

```bash
TCS_COOKIES={"session": "dein_session_wert_hier", "auth_token": "dein_token_wert_hier"}
```

**Wichtig:**
- Muss ein gültiges JSON sein
- Doppelte Anführungszeichen für Keys und Values
- Keine Zeilenumbrüche im Cookie-Wert

### Beispiel:
```bash
TCS_COOKIES={"session": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"}
```

## Schritt 6: Portainer Environment Variables

Wenn du via Portainer deployst:

1. Stack öffnen → **Environment variables**
2. Neues Variable hinzufügen:
   - **Name**: `TCS_COOKIES`
   - **Value**: `{"session": "...", "auth_token": "..."}`

## Troubleshooting

### Cookie funktioniert nicht?
- **Abgelaufen?** Manche Cookies haben eine Lifetime. Schau in den DevTools nach "Expires"
- **Falsches Domain?** Cookie muss für `.tcs.ch` oder `benzin.tcs.ch` gelten
- **Secure-Flag?** Cookie wird nur über HTTPS gesendet

### Welche Cookies brauche ich wirklich?
Das musst du ausprobieren. Starte mit dem `session` Cookie, falls vorhanden.

## Alternative: Browser Extension

Es gibt Extensions, die alle Cookies als JSON exportieren:
- Chrome: "EditThisCookie"
- Firefox: "Cookie-Editor"

Diese machen den Export einfacher!
