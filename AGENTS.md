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

## Projektziel: Posylka

Open WebUI soll als KI-Arbeitsumgebung fuer **Posylka** dienen. In der
Anwendung soll ein eigener Projektbereich mit dem Namen **Posylka** fuer
projektbezogene Chats, Anweisungen und Wissen eingerichtet werden. Das
OpenChamber-Codeprojekt **Open WebUI** und dieser Anwendungsbereich sind
unterschiedliche Dinge; das Codeprojekt nicht dafuer umbenennen.

Gewuenschte Anbindungen:

- **OpenAI ueber den vorhandenen ChatGPT-Pro-Account**, nicht automatisch
  ueber eine separat abgerechnete OpenAI-API. Einen fuer die eingesetzte
  Version unterstuetzten Kontozugang pruefen. Ein WebUI-SSO-Login allein
  stellt keinen Modellzugang bereit. Kein API-Guthaben aus dem Pro-Abo
  ableiten und keine freie Nutzung aller API-Modelle versprechen.
- **Higgsfield MCP fuer Bilder**, insbesondere Bildgenerierung und
  Bildbearbeitung im Posylka-Arbeitsablauf. Offizieller Remote-Endpunkt:
  `https://mcp.higgsfield.ai/mcp`. Anmeldung ueber Higgsfield-OAuth mit dem
  vorgesehenen Benutzerkonto; kein separater Higgsfield-API-Key notwendig.
  Die Kompatibilitaet des WebUI-MCP-/OAuth-Clients mit dem Dienst vor einer
  Erfolgsmeldung pruefen. Keine OpenCode-MCP-Konfiguration als Ersatz fuer
  die Anbindung innerhalb von Open WebUI behandeln.

### Umsetzung und Abnahme

1. Vorhandene Projekt-/Ordnerfunktionen und bestehende Bereiche pruefen;
   Posylka nicht doppelt anlegen. Zielkonto und Sichtbarkeit klaeren, falls
   sie aus der angemeldeten Sitzung nicht eindeutig hervorgehen. Mit einem
   privaten Bereich beginnen; keine pauschale Freigabe an alle Benutzer.
2. Projektanweisungen und Wissen nur aus bestaetigten Posylka-Informationen
   uebernehmen. Keine Firmendaten, Markenregeln oder Dokumente erfinden.
3. Fuer ChatGPT Pro einen nachweislich unterstuetzten Integrationsweg
   ermitteln. Falls ein zusaetzlicher Adapter notwendig ist, Architektur,
   Nutzungsbedingungen, Kontorisiken und Betriebsaufwand vor Installation
   mit dem Benutzer abstimmen. Kein stiller Wechsel zur kostenpflichtigen
   API und kein Kopieren bestehender Codex-/OpenCode-Anmeldedaten.
4. Higgsfield innerhalb von Open WebUI als MCP-Werkzeug anbinden und die
   persoenliche OAuth-Freigabe vom Benutzer durchfuehren lassen. Tokens
   ausschliesslich geschuetzt im Laufzeitsystem speichern, niemals in
   Projektdateien, Chat-Ausgaben oder Logs offenlegen.
5. Higgsfield-MCP-Generierungen verbrauchen laut Anbieter immer Credits;
   Unlimited- und Gratisgenerierungen der Website gelten dort nicht.
   Vor einem kostenpflichtigen Generierungstest Zustimmung einholen;
   kein Abo abschliessen, keine Credits kaufen und keine kostenpflichtige
   Testphase ohne gesonderten Auftrag aktivieren.
6. Abnahme in der echten Oberflaeche: Posylka sichtbar, Modellantwort ueber
   den gewaehlten Pro-Zugang, Higgsfield verbunden und Werkzeuge abrufbar.
   Nach freigegebenem Bildtest Ergebnisanzeige pruefen. Konfiguration,
   ausstehende Anmeldung und erfolgreich getesteten Betrieb klar trennen.

### Verifizierter Stand der Vorbereitung (2026-10-26)

- Die Ziele Posylka, ChatGPT Pro und Higgsfield sind vom Benutzer bestaetigt.
- Im untersuchten Backend dieses Checkouts wurde kein nativer
  ChatGPT-/Codex-Kontozugang gefunden. Der Pro-Integrationsweg ist offen;
  die normale OpenAI-API-Verbindung ist kein Ersatz fuer diese Anforderung.
- Der Higgsfield-Endpunkt, OAuth und Creditverbrauch sind durch die
  offizielle Anbieter-Dokumentation bestaetigt. Die Verbindung mit dieser
  Open-WebUI-Installation ist noch nicht getestet oder eingerichtet.
- Die Anlage von Posylka in der laufenden Anwendung ist noch nicht
  verifiziert. Der OpenChamber-Browserzugriff lieferte bei der Vorbereitung
  HTTP 401; daraus folgt keine Aussage ueber den Zustand der Anwendung.

Quellen fuer die Anbindungen:

- OpenAI: `https://help.openai.com/en/articles/20001542-using-your-chatgpt-plan-in-other-apps-and-sites`
- Open WebUI: `https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai.md`
- Higgsfield: `https://higgsfield.ai/creator-hub/help-center/integrations/what-is-higgsfield-mcp`

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
