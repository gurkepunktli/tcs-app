# Cloudflared Container in Portainer erstellen

Anleitung zum Erstellen eines einzelnen Cloudflared Tunnel Containers (kein Stack) in Portainer mit Token-Authentifizierung.

## Voraussetzungen

1. Cloudflare Zero Trust Account
2. Tunnel in Cloudflare Dashboard erstellt
3. Tunnel Token bereit

### Tunnel Token besorgen

1. **Cloudflare Dashboard** → **Zero Trust** → **Networks** → **Tunnels**
2. Klick auf **Create a tunnel**
3. Wähle **Cloudflared**
4. Name eingeben (z.B. `tcs-backend-tunnel`)
5. **Connector wird angezeigt** → Token kopieren

Der Token sieht aus wie: `eyJhIjoiTXlBY2NvdW50VGFnMTIzIiwidCI6Ik15VHVubmVsSUQxMjMiLCJzIjoiTXlUdW5uZWxTZWNyZXQxMjMifQ==`

---

## Methode 1: Container mit Environment Variable (Empfohlen)

### Schritt 1: Container erstellen

1. **Portainer** → **Containers** → **Add container**

### Schritt 2: Basis-Konfiguration

**Name:**
```
cloudflared-tunnel
```

**Image:**
```
cloudflare/cloudflared:latest
```

### Schritt 3: Command

**Command:**
```
tunnel run
```

**WICHTIG:** Nutze NUR `tunnel run`, NICHT `tunnel run --token ...`

### Schritt 4: Environment Variables

Klick auf **+ add environment variable**

**Name:**
```
TUNNEL_TOKEN
```

**Value:**
```
eyJhIjoiTXlBY2NvdW50VGFnMTIzIiwidCI6Ik15VHVubmVsSUQxMjMiLCJzIjoiTXlUdW5uZWxTZWNyZXQxMjMifQ==
```

(Ersetze mit deinem echten Token)

### Schritt 5: Network Settings

**Network:**
- Wähle dein bestehendes Netzwerk (z.B. `fiber.x_net`)
- Oder lass es auf `bridge`

**Restart policy:**
```
Unless stopped
```

### Schritt 6: Deploy

Klick auf **Deploy the container**

---

## Methode 2: Container mit Token im Command

Falls Environment Variable nicht funktioniert, nutze Token direkt im Command.

### Schritt 1-2: Wie oben

### Schritt 3: Command mit Token

**Command:**
```
tunnel --no-autoupdate run --token eyJhIjoiTXlBY2NvdW50VGFnMTIzIiwidCI6Ik15VHVubmVsSUQxMjMiLCJzIjoiTXlUdW5uZWxTZWNyZXQxMjMifQ==
```

**WICHTIG:** Ersetze den Token mit deinem echten Token!

### Schritt 4-6: Wie oben

**WARNUNG:** Diese Methode ist weniger sicher, da der Token im Command sichtbar ist.

---

## Methode 3: Mit User Root (bei Permission-Problemen)

### Advanced container settings → User

**User:**
```
root
```

Manchmal nötig, wenn der Container keine Permissions hat.

---

## Tunnel konfigurieren (Public Hostname)

Nachdem der Container läuft:

1. **Cloudflare Dashboard** → **Zero Trust** → **Networks** → **Tunnels**
2. Wähle deinen Tunnel
3. **Public Hostname** → **Add a public hostname**

**Beispiel für TCS API:**

- **Subdomain:** `tcs-api`
- **Domain:** `deine-domain.com`
- **Service:**
  - Type: `HTTP`
  - URL: `tcs-ocr-api:8000` (Container-Name:Port)

Oder wenn nicht im gleichen Netzwerk:
  - URL: `http://172.17.0.1:8000` (Docker Host IP)

---

## Container prüfen

### Logs ansehen

```bash
docker logs cloudflared-tunnel
```

Erwartete Ausgabe:
```
2025-12-25T12:00:00Z INF Starting tunnel tunnelID=...
2025-12-25T12:00:01Z INF Connection registered connIndex=0
2025-12-25T12:00:01Z INF Connection registered connIndex=1
```

### Container Status

In Portainer:
- **Containers** → `cloudflared-tunnel`
- Status sollte **running** sein

---

## Troubleshooting

### Container startet nicht

**Logs prüfen:**
```bash
docker logs cloudflared-tunnel
```

**Häufige Fehler:**

1. **Invalid token:**
   ```
   ERR error="Unauthorized: Invalid token" connIndex=0
   ```
   → Token ist falsch oder abgelaufen

2. **Tunnel not found:**
   ```
   ERR error="Tunnel not found" tunnelID=...
   ```
   → Tunnel wurde in Cloudflare Dashboard gelöscht

3. **Permission denied:**
   ```
   ERR error="Permission denied"
   ```
   → Container mit `user: root` starten

### Tunnel verbindet nicht

1. **Firewall:** Port 7844 (UDP) muss offen sein
2. **Network:** Container muss im gleichen Netzwerk wie Backend sein
3. **Internet:** Cloudflared braucht ausgehenden Internet-Zugang

### Service nicht erreichbar

1. **Service URL prüfen:** Muss `containername:port` sein
2. **Network prüfen:** Beide Container im gleichen Netzwerk?
3. **Service läuft:** Backend Container ist running?

```bash
# Teste von cloudflared Container aus:
docker exec cloudflared-tunnel wget -O- http://tcs-ocr-api:8000/health
```

---

## Best Practices

### Sicherheit

- ✅ Nutze Environment Variable für Token (nicht Command)
- ✅ Setze `restart: unless-stopped`
- ✅ Nutze aktuelles Image: `cloudflare/cloudflared:latest`
- ❌ Teile Token nie öffentlich

### Performance

- Nutze gleiche Docker Network für alle Container
- Cloudflared braucht wenig Ressourcen (keine Limits nötig)

### Monitoring

```bash
# Logs live ansehen:
docker logs -f cloudflared-tunnel

# Container Stats:
docker stats cloudflared-tunnel
```

---

## Beispiel: TCS Backend via Tunnel

### Container Setup

1. **Name:** `cloudflared-tunnel`
2. **Image:** `cloudflare/cloudflared:latest`
3. **Command:** `tunnel run`
4. **Env:** `TUNNEL_TOKEN=dein_token_hier`
5. **Network:** `fiber.x_net`
6. **Restart:** `unless-stopped`

### Cloudflare Tunnel Config

**Public Hostname:**
- Subdomain: `tcs-api`
- Domain: `example.com`
- Service Type: `HTTP`
- URL: `tcs-ocr-api:8000`

**Ergebnis:** `https://tcs-api.example.com` → `http://tcs-ocr-api:8000`

---

## Quellen

- [cloudflare/cloudflared Docker Image](https://hub.docker.com/r/cloudflare/cloudflared)
- [Cloudflare Tunnel Parameters](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/cloudflared-parameters/run-parameters/)
- [Cloudflare Tunnel with Docker Guide](https://thedxt.ca/2022/10/cloudflare-tunnel-with-docker/)
- [Portainer with Cloudflare](https://medium.com/@portainerio/protecting-portainer-and-edge-devices-with-cloudflare-8a98bc556a78)
