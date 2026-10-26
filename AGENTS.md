# Open WebUI — ai.colibo.io

## Auftrag und Arbeitsverzeichnis

Dies ist die bearbeitbare Open-WebUI-Arbeitskopie auf `tposylka`:
`/var/www/open-webui`, Branch `colibo`, Ausgangsversion `v0.12.4`.
Die OpenChamber zeigt sie als Projekt **Open WebUI**.

- Frontend: `src/` (Svelte/TypeScript), statische Dateien `static/`.
- Backend: `backend/open_webui/` (Python/FastAPI).
- Eigene Betriebsdateien und Anleitung: `hosting/README.md`.
- Live-Stack und Daten: `/opt/docker/open-webui`, nicht dieser Checkout.
- Oeffentliche Instanz: `https://ai.colibo.io`.

## Verbindliche Regeln

1. Kein Commit, Push, Image-Build oder Deploy ohne ausdruecklichen Auftrag.
   `origin` ist der oeffentliche Fork `fuchs-alexander/open-webui`; `upstream`
   ist `open-webui/open-webui` mit absichtlich auf `DISABLED` gesetztem Push-URL.
   Der Branch `colibo` folgt `origin/colibo`. Keine Projektdateien automatisch
   veroeffentlichen; auch der Fork ist oeffentlich. Kein Push auf den Upstream.
2. Vor Aenderungen `git status` lesen, fremde Arbeit erhalten. Keine destruktiven
   Git-Befehle und niemals `docker compose down -v` oder Datenvolumes loeschen.
3. **Nicht** das Upstream-`docker-compose.yaml` zum Starten verwenden: es ist nicht
   die Colibo-Konfiguration und koennte zusaetzliche Dienste starten.
4. Das laufende offizielle Image liest diesen Quellcode nicht. Codeaenderungen
   werden erst durch einen ausdruecklichen Build/Deploy wirksam.
5. Secrets und Laufzeitdaten bleiben ausserhalb dieses Checkouts. `.env` unter
   `/opt/docker/open-webui/.env` nicht ausgeben, kopieren oder committen.
   Keine Ausgabe von `docker inspect` mit der gesamten ENV oder von ungefiltertem
   `docker compose config`. Nur `config --quiet` fuer Validierung verwenden.
6. Vor jedem Live-Deploy konsistent sichern. Nur Open WebUI anfassen; der gemeinsame
   nginx bedient weitere Posylka-Anwendungen und darf nicht neu erzeugt werden.
7. nginx-Aenderungen nur am vhost `ai.colibo.io`, vorher sichern, `nginx -t`
   pruefen und dann neu laden. Andere vhosts unveraendert lassen.
8. Die KI-Anbindung ist offen: gewuenscht ist **ChatGPT Pro**, nicht eine separat
   abgerechnete OpenAI-API. Keine API-Schluessel erfinden und keine vorhandenen
   Codex-/OpenCode-Credentials fuer einen anderen Dienst kopieren.
9. Registrierung geschlossen und Authentifizierung aktiv lassen. Open-WebUI-
   Kennzeichnungen und Lizenzbedingungen des Upstreams respektieren.
10. `opencode` nicht als zusaetzlichen Hintergrundserver starten. Fuer Arbeiten
    die bestehende OpenChamber-Session benutzen.

## Pruefung

`./hosting/project.sh check` prueft Compose, Quellcode-Build-Konfiguration und
Shell-Syntax ohne Build oder Neustart. `status` und `logs` sind ebenfalls lesend.
`backup` fuehrt eine ausdruecklich angeforderte Sicherung mit kurzer App-Pause aus.

Nach einem beauftragten Deploy HTTPS, Login, geschlossenen Signup, WebSockets,
Container-Health und die bestehenden Nachbar-Domains pruefen. Ein erfolgreicher
Healthcheck allein beweist keine funktionierende Browseroberflaeche.
