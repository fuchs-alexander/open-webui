# Open WebUI auf ai.colibo.io bearbeiten

Dieses Projekt ist eine echte Quellcode-Arbeitskopie von Open WebUI **v0.12.4**,
dem Stand der installierten Anwendung. Du kannst hier mit OpenChamber sowohl
die Oberflaeche als auch Backend und Hosting-Konfiguration anpassen.

## Einstieg

| Bereich | Datei/Verzeichnis |
|---|---|
| Oberflaeche | `src/lib/components/`, `src/routes/` |
| Uebersetzungen | `src/lib/i18n/` |
| Backend/API | `backend/open_webui/` |
| Containerbau | `Dockerfile` im Projektwurzelverzeichnis |
| Colibo-Betriebseinstellungen | `hosting/compose.yaml` |
| HTTPS-/Proxy-Einstellungen | `hosting/ai.colibo.io.conf` |
| Eigenes Image bauen | `hosting/compose.source.yaml` |
| Lesende Pruefungen | `hosting/project.sh` |

Branch: `colibo`, folgt `origin/colibo` auf Basis von Open WebUI `v0.12.4`.

- `origin`: eigener oeffentlicher Fork <https://github.com/fuchs-alexander/open-webui>,
  Git-Zugang per `git@github.com:fuchs-alexander/open-webui.git`.
- `upstream`: Original <https://github.com/open-webui/open-webui>, nur zum Lesen.
  Dessen Push-URL bleibt absichtlich auf `DISABLED` gesetzt.
- Eigener SSH-Deploy-Key auf `tposylka`, Schreibrecht ausschliesslich auf den Fork.
  Privater Key und verifizierte GitHub-Hostkeys liegen ausserhalb des Checkouts
  unter `/root/.ssh/`; `core.sshCommand` waehlt sie pro Repository aus.

Der Branch `colibo` basiert auf dem bestehenden v0.12.4-Upstream-Commit. Die
Colibo-Ergaenzungen liegen in `AGENTS.md` und `hosting/`; der Anwendungscode
selbst ist bislang unveraendert. Commits und Pushes nur auf ausdruecklichen
Auftrag; der Fork ist **nicht privat**.

## Was bereits laeuft

Der Live-Stack bleibt unter `/opt/docker/open-webui`; dort liegen die geheime
`.env` und `data/` mit Benutzern, Chats und Uploads. Fuer den Anzeigenamen
**PosylkaAI** laeuft seit dem freigegebenen Deploy vom 26.10.2026 das lokale
Image `open-webui-posylkaai:v0.12.4-branding`. Es basiert auf dem zuvor
laufenden offiziellen v0.12.4-Digest
und ersetzt ausschliesslich `backend/open_webui/env.py`; Frontend und
Abhaengigkeiten bleiben unveraendert. Den tatsaechlichen Live-Stand mit
`./hosting/project.sh status` pruefen.

**Aenderungen hier werden nicht automatisch live.** Eine neue Chat-Session in
diesem Projekt kann sie vorbereiten und pruefen; Build/Deploy nur nach Auftrag.
Keine Laufzeitdaten oder Zugangsdaten in dieses Repository kopieren.

```bash
./hosting/project.sh check
./hosting/project.sh status
./hosting/project.sh logs
```

`check` verwendet bewusst `/opt/docker/open-webui` als Compose-Projektverzeichnis.
So werden `.env` und `data/` an den bestehenden Live-Pfaden aufgeloest statt als
neue Dateien im Checkout angelegt. Niemals das Upstream-Compose unbesehen starten.

## Aenderungen spaeter veroeffentlichen

Vorher Diff pruefen und ein Backup ausdruecklich starten:

```bash
./hosting/project.sh backup
```

Die Sicherung unterbricht nur Open WebUI kurz und wartet auf dessen Healthcheck.
Sie liegt lokal unter `/backup/open-webui`; kein Offsite-Backup vorhanden.

### Nur Betriebseinstellungen

Nach ausdruecklichem Deploy-Auftrag `hosting/compose.yaml` geschuetzt nach
`/opt/docker/open-webui/compose.yaml` uebernehmen und dort gezielt
`docker compose up -d --wait --wait-timeout 180 open-webui` ausfuehren.
Vorhandenen Live-Stand vorher separat sichern. Ein reines `restart` uebernimmt
keine geaenderten Environment-Werte.

### Eigene Frontend-/Backend-Aenderungen

#### Nur der Anzeigename PosylkaAI

Die Umbenennung ohne automatischen Zusatz nutzt die Branding-Ausnahme der
Open-WebUI-Lizenz: hoechstens 50 Endnutzer innerhalb rollierender 30 Tage.
Zum Zeitpunkt der Pruefung waren drei Benutzer registriert. Vor Wachstum
ueber diese Grenze Branding zuruecknehmen oder die erforderliche Erlaubnis
einholen. Logos, Copyright- und Lizenzdateien werden nicht entfernt.

```bash
python3 -m unittest discover -s hosting/tests -v
docker build -f hosting/Dockerfile.branding \
  -t open-webui-posylkaai:v0.12.4-branding .
```

Der Dockerfile-spezifische Build-Kontext enthaelt keine Runtime-Secrets,
Gateway-Dateien oder anderen Projektinhalte. Der Basis-Digest ist gepinnt;
vor spaeteren Upgrades muss `env.py` erneut mit dem neuen Basisstand
abgeglichen werden. Das Branding-Image ist kein vollstaendiger Source-Build:
weitere Quellcodeaenderungen werden dadurch nicht mit veroeffentlicht.

Nach gesondertem Deploy-Auftrag nur Image und `WEBUI_NAME` in der bestehenden
Live-Compose-Datei aktualisieren, andere parallel geaenderte Einstellungen
erhalten. Der normale Backup-Umfang erfasst diese Compose-Konfiguration;
fuer Wiederherstellung ausserdem das lokale Image aufbewahren oder aus dem
gepinnten Basisimage und dem dokumentierten Source-Stand neu bauen.

#### Vollstaendiger Source-Build

Der optionale Source-Override baut den Code aus `/var/www/open-webui` zum lokalen
Image `open-webui-colibo:local`. Nur nach ausdruecklichem Build-Auftrag:

```bash
docker compose --project-directory /opt/docker/open-webui \
  -f /var/www/open-webui/hosting/compose.yaml \
  -f /var/www/open-webui/hosting/compose.source.yaml build open-webui
```

Der Build alleine aendert den laufenden Container nicht. Ein anschliessender
Deploy muss beide Compose-Dateien bewusst uebernehmen/verwenden, das gewaehlte
Image und den Build-Stand dokumentieren und den Backup-Umfang um den Source-
Override erweitern. Dieser Source-Build/Deploy wurde bei der Projektanlage
**nicht** ausgefuehrt; der Source-Override wurde nur mit Compose validiert.

### Proxy und Wartung

Live-vhost:
`/var/www/posylka.de/.docker/nginx/etc/sites-enabled.test/ai.colibo.io.conf`.
Nach beauftragter Aenderung nur diesen vhost sichern/uebernehmen, dann
`docker exec nginx nginx -t` und `docker exec nginx nginx -s reload`.
Der gemeinsame nginx darf nicht neu erzeugt werden.

Das Backup-Skript laeuft als `/usr/local/sbin/open-webui-backup`; Timer und Service
liegen unter `/etc/systemd/system/open-webui-backup.{timer,service}`.
Die entsprechenden Dateien in `hosting/` sind bearbeitbare Vorlagen und werden
nicht automatisch installiert.

## Offene Punkte

- ChatGPT-Pro-Anbindung noch nicht eingerichtet. Native SIWC-Unterstuetzung oder
  passenden Adapter und Tarif-/Modellgrenzen vor der Anbindung pruefen.
- Der zuvor gemeldete 500-Fehler war bei der Nachpruefung nicht reproduzierbar;
  keine bestaetigte Ursache oder Entwarnung durch den Benutzer.
- Betriebseinstellungen in Open WebUI koennen intern persistent gespeichert sein.
  Ein geaenderter Compose-ENV-Wert ueberschreibt solche UI-Einstellungen nicht
  automatisch. Secrets weiterhin ausschliesslich im Live-Stack halten.

Weitere Betriebsdokumentation: `docs/open-webui.md` im separaten Hosting-Repo
`/var/www/nomobo-hosting` auf der Control-Plane. Dort werden die urspruenglichen
Hosting-Vorlagen gepflegt; Aenderungen im Posylka-Checkout bei Bedarf bewusst
zurueckfuehren, nicht blind gegenseitig ueberschreiben.
