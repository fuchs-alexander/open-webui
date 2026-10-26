# CLIProxyAPI fuer Posylka

Status: Architekturentwurf zur Benutzerfreigabe; noch nicht implementiert.
Stand: 2026-10-26.

## Ziel und bestaetigter Auftrag

Alle angemeldeten Open-WebUI-Benutzer sollen ueber einen gemeinsamen
ChatGPT-Pro-Account arbeiten. Claude soll ebenfalls mit einem Abo-Login
ueber dieselbe Gateway-Infrastruktur nutzbar werden. Der Benutzer hat
CLIProxyAPI ausgewaehlt. Keine separat abgerechnete OpenAI-/Anthropic-API,
kein OpenRouter-Fallback und keine automatische kostenpflichtige Ausweichroute.

Ein gemeinsamer Account bedeutet gemeinsame Providerlimits, nicht ein
eigenstaendiges Nutzungskontingent je WebUI-Benutzer. Die technischen
Gateway-Funktionen begruenden keine Mehrbenutzerlizenz beim Provider.
Anbieterbedingte Sperren oder Ablehnungen werden angezeigt, nicht umgangen.

## Ist-Zustand

- Open WebUI v0.12.4 laeuft unter `https://ai.colibo.io`.
- Der Live-Stack liegt unter `/opt/docker/open-webui`.
- Der Container ist am Netz `open-webui_default` angeschlossen.
- Die Checkout-Vorlage deaktiviert OpenAI-Verbindungen; persistente
  Laufzeiteinstellungen sind vor einer Aenderung separat zu pruefen.
- Posylka ist als privater Bereich angelegt. Higgsfield MCP ist fuer alle
  angemeldeten Benutzer freigegeben, mit jeweils persoenlicher OAuth-Sitzung.
- Fremde Aenderungen an `AGENTS.md` und die Recherchedateien bleiben erhalten.

## Entscheidung und Alternativen

Gewaehlter Aufbau: ein kleiner CLIProxyAPI-Dienst ohne zusaetzliche
Governance-Plattform. OmniRoute waere umfangreicher; LiteLLM davor wuerde
eine zweite Konvertierungs- und Betriebsschicht schaffen. Beides wird nicht
installiert. OpenRouter bleibt ausserhalb dieses Auftrags, da es keinen
vergleichbaren Abo-Login als Upstream anbietet.

## Komponenten und Datenfluss

1. Browser -> bestehendes Open WebUI mit unveraenderter Authentifizierung.
2. WebUI-Backend -> `http://cliproxyapi:8317/v1` im privaten Docker-Netz,
   abgesichert durch einen neuen, ausschliesslich dafuer erzeugten Gateway-Key.
3. CLIProxyAPI -> angemeldeter ChatGPT- beziehungsweise Claude-Provider.
4. Higgsfield-Werkzeuge werden weiterhin von WebUI ausgefuehrt; ihr Ergebnis
   geht in den naechsten Modellturn. Kein zusaetzlicher Higgsfield-Connector
   im Gateway und kein providerseitiges Hosted-MCP als Ersatz.

Ein eigener Compose-Stack verwendet das bestehende WebUI-Netz als externes
Netz. Er veraendert weder gemeinsame nginx-Dienste noch andere Anwendungen.
Der Gateway-Inferenzport wird nicht auf dem Host veroeffentlicht. Das
bestehende Netz erfordert weiterhin Authentifizierung zwischen Diensten;
Netzmitgliedschaft allein gilt nicht als Zugangsschutz.

## Version, Dateien und Geheimnisse

- Ausgangspunkt ist der recherchierte Mainline-Release v8.0.43. Vor dem
  Start Image-Verfuegbarkeit, Herkunft und Digest gegen den Release pruefen;
  kein `latest`, kein ungepruefter Fork und kein stilles Source-Build.
- Bearbeitbare, geheimnisfreie Vorlagen und Betriebsanleitung werden unter
  `hosting/` gepflegt, einschliesslich Compose-/Gateway-Konfigurationsvorlage.
- Laufzeitdateien liegen getrennt unter `/opt/docker/cliproxyapi`;
  Auth-Verzeichnis und Backups sind nur fuer den Betreiber lesbar.
- Provider-Tokens und produktive Gateway-Keys werden weder im Repository
  noch in dieser Spezifikation, Chat-Ausgaben oder Supportlogs gespeichert.
- Kein Docker-Socket, keine privilegierten Container, keine Cloud-Synchronisation,
  Plugins, Fernverwaltung oder automatische Panel-Updates ohne Bedarf.
- Prozess-/Speicherlimits und begrenzte Logs; Request-/Response-Body-Logging aus.
- Management bleibt deaktiviert, sofern fuer den getesteten Loginpfad nicht
  erforderlich. Falls erforderlich: getrennte Authentifizierung und nur
  ueber einen zeitlich begrenzten Betreiberzugang, nie oeffentlich.

## Frische Kontoanmeldung

Vorhandene Codex-/OpenCode-/Claude-Code-Credentials werden nicht gelesen,
kopiert oder eingebunden. Der Benutzer bestaetigt neue Provideranmeldungen
selbst auf der jeweiligen offiziellen Anmeldeseite.

OpenAI: Der getaggte CLIProxyAPI-Code bietet `codex-login` beziehungsweise
`codex-device-login` fuer eine neue gatewayeigene Registrierung. Der
getaggte `siwc-bind`-Pfad benoetigt anschliessend eine bestehende
gatewayeigene Codex-Datei und ergaenzt diese durch eine neue SIWC-Freigabe.
Es wird nicht behauptet, dass dieser Release einen unabhaengigen
Ein-Schritt-SIWC-Erstlogin anbietet. Nach der Bindung muss der tatsaechliche
Inferenzweg die oeffentliche Responses API nutzen. Bei SIWC-Fehlern keine
unbemerkte Rueckkehr zum Legacy-Codex-Weg oder zu einem bezahlten API-Key.

Claude: Der getaggte Entrypoint bietet `claude-login`; frische Anmeldung,
Persistenz und Refresh sind vor WebUI-Freischaltung praktisch nachzuweisen.
Kein Tokenimport als vermeintlicher Erstlogin. Keine Anpassung zur Umgehung
einer Anbieterablehnung oder zur Verschleierung der Anwendung.

Loopback-OAuth benoetigt einen Callback zum Server, nicht zum Benutzer-PC.
Der Betreiber verwendet dafuer einen SSH-Loopback-Tunnel zum passenden
Callback-Listener. Exakte Portbindung wird anhand des ausgewaehlten Release
und der Containerlaufzeit vor dem Login verifiziert. Keine zusaetzliche
oeffentliche Callback-Route und keine Callback-Codes im Chat. Falls kein
sicherer Rueckkanal verfuegbar ist, bleibt der Stand explizit
"installiert, Anmeldung ausstehend" statt "fertig".

## WebUI-Verbindung und Modellfreigabe

Bestehende Verbindungseinstellungen per authentifizierter Admin-API lesen
und vor dem Update geschuetzt sichern. Neue Gateway-Verbindung ergaenzen,
keine anderen Verbindungen oder MCP-Konfigurationen ueberschreiben.
`ENABLE_OPENAI_API` gezielt aktivieren und Persistenz bei Neustart pruefen.
Wenn ein Neustart erforderlich ist, nur Open WebUI betreffen.

Modelle erst nach erfolgreichem Login aus dem konkreten Konto ermitteln;
keine Modellnamen oder Verfuegbarkeit erfinden. OpenAI und Claude eindeutig
kennzeichnen, damit kein unbeabsichtigter Providerwechsel erfolgt. Die
freigegebenen Modelle sollen fuer alle angemeldeten Benutzer sichtbar sein.
Keine oeffentliche anonyme Nutzung. Kein Versprechen persoenlicher Quoten
bei einer zentralen Gateway-Verbindung.

## Sicherung und Rueckweg

Vor Live-Aenderungen eine konsistente WebUI-Sicherung einschliesslich
persistenter Einstellungen mit dem bestehenden Backup-Verfahren erstellen;
die kurze WebUI-Pause im Umsetzungsplan sichtbar machen. Gatewaykonfiguration,
Version/Digest und Auth-Verzeichnis separat geschuetzt sichern. Provider-Tokens
nicht in offen zugaengliche Diagnosearchive aufnehmen.

Rueckweg: WebUI-Gateway-Verbindung deaktivieren und nur die geaenderten
Verbindungseinstellungen auf den gesicherten Stand setzen. Gateway stoppen,
ohne Volumes oder WebUI-Daten zu loeschen. Kein vollstaendiger Datenbankrestore,
der zwischenzeitliche Chats ueberschreibt, ohne gesonderte Abstimmung.

## Abnahmekriterien

1. Compose-/Shell-Pruefung ohne Secrets-Ausgabe; Image und Versionsflags
   entsprechen dem gepinnten Release. Keine neuen oeffentlichen Ports.
2. Gateway lehnt Requests ohne beziehungsweise mit falschem Key ab.
3. Frischer Login je Provider, Modellliste und einfache Antwort funktionieren;
   ChatGPT verwendet SIWC. Keine bezahlten Provider oder Fallbacks konfiguriert.
4. Streaming, lange Historie, Chat-Titel-Hintergrundanfragen und zwei parallele
   WebUI-Sitzungen funktionieren ohne Kontextvermischung.
5. Neustart erhaelt Konfiguration und Kontozugang. Refresh pruefen; falls
   echter Tokenablauf noch nicht beobachtet wurde, diese Einschraenkung melden.
6. Planlimits, Widerruf und Providerfehler werden klar behandelt. Kein
   Accountwechsel oder Retry-Sturm zur Umgehung von Limits.
7. WebUI-seitiger Function-Tool-Zyklus einschliesslich zweitem Modellturn
   funktioniert. Higgsfield-Discovery nach persoenlicher Freigabe pruefen;
   keine Bildgenerierung ohne gesonderte Credit-Zustimmung.
8. HTTPS, Login, geschlossener Signup, WebSockets, Containerzustand und
   bestehende Nachbar-Domains bleiben funktionsfaehig. UI-Abnahme nur dann
   behaupten, wenn sie wirklich durchgefuehrt werden konnte.

## Freigabe und naechster Schritt

Dieser Entwurf ist noch kein erfolgreiches Deployment. Nach Benutzerpruefung
folgt der konkrete Umsetzungs- und Testplan, danach die Umsetzung. Kein
Commit oder Push ohne ausdruecklichen Auftrag. Unmoegliche Provideranmeldungen
oder fehlende Benutzerfreigaben werden als Blocker benannt, nicht durch eine
andere Abrechnungsart ersetzt.

## Quellen

- Recherche: `reports/KI Gateways fuer Posylka.md` (Dateiname im Repository mit Umlaut).
- https://github.com/router-for-me/CLIProxyAPI/releases/tag/v8.0.43
- https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.43/cmd/server/main.go
- https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.43/internal/cmd/siwc_bind.go
- https://developers.openai.com/siwc/token-sharing-open-source
- https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations
