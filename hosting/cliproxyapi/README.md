# CLIProxyAPI-Gateway fuer Open WebUI

Seit 2026-10-26 nutzt `https://ai.colibo.io` einen gemeinsamen ChatGPT-Pro-Account
und ein Claude-Abo ueber CLIProxyAPI. Entwurf:
`docs/superpowers/specs/2026-10-26-cliproxyapi-design.md`.

Ein gemeinsamer Account bedeutet gemeinsame Providerlimits fuer alle WebUI-Benutzer.
Gegenueber dem Provider ist jeder Request derselbe Account; wer was ausgeloest hat,
steht nur in Open WebUI. Kein bezahlter API-Key, kein OpenRouter, kein Fallback.

## Bestand

| | |
|---|---|
| Image | `eceasy/cli-proxy-api:v8.0.43@sha256:3f74ca56cba8bea2a2a096a215bb774482d87d257da04c5047e6046493bfd644`, Commit `3078035` = Release-Tag |
| Live-Stack | `/opt/docker/cliproxyapi` (0700): `compose.yaml`, `config.yaml` (0400, uid 10001), `auths/` (0700) |
| Netz | extern `open-webui_default`; WebUI erreicht `http://cliproxyapi:8317/v1`. Kein Host-Port. |
| Container | uid 10001, read-only rootfs, `cap_drop: ALL`, `no-new-privileges`, 512 MB, 1 CPU, 256 PIDs, Logs 3 x 10 MB |
| Gateway-Key | nur in `config.yaml` und in der WebUI-Verbindung (Datenbank). Nie ins Repo. |
| ChatGPT | `codex-…-chatgpt@posylka.com-pro.json`, `use_siwc: true`; Inferenz ueber `api.openai.com/v1` (SIWC) |
| Claude | `claude-…-alexander.fuchs@posylka.com.json` |

Abgeschaltet: Management-API und Panel, Plugins, LAN-Discovery, Request-Logging,
Nutzungsstatistik, Bildgenerierung, Wiederholungsrunden (`request-retry: 0`),
Codex- und Claude-Cloaking. Ist SIWC aktiv und fehlt das SIWC-Token, antwortet das
Gateway mit 401 statt auf den Legacy-Codex-Weg zu wechseln.

**Body-Logs:** Bei Fehlern schreibt CLIProxyAPI unabhaengig von `request-log`
erzwungene Fehler-Logs mit Request-Body. Ist `./logs` nicht beschreibbar, weicht es
auf `<auth-dir>/logs` aus. `WRITABLE_PATH=/CLIProxyAPI` lenkt das ins schreibgeschuetzte
Image; dort schlaegt das Schreiben fehl, `auths/` bleibt frei von Gespraechsinhalten.

## Freigegebene Modelle

Verbindung `http://cliproxyapi:8317/v1`, Tag `Posylka-Gateway`, `model_ids` auf diese
11 begrenzt. Jedes Modell hat einen WebUI-Eintrag mit Lesezugriff fuer alle angemeldeten
Benutzer (`user:*`), Tag `ChatGPT` oder `Claude`, Name mit Provider-Praefix:

- ChatGPT: `gpt-6.1-sol`, `gpt-6-sol`, `gpt-6-astra`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`
- Claude: `claude-opus-5-5`, `claude-fable-5-1`, `claude-sonnet-5-5`, `claude-haiku-5-5`

Nicht freigegeben: Bildmodelle (`gpt-image-*`, auf `/chat/completions` nicht nutzbar),
`codex-auto-review` und aeltere Claude-Modelle.

## Betrieb

```bash
./hosting/cliproxyapi/cliproxyapi.sh check    # Compose/Shell pruefen
./hosting/cliproxyapi/cliproxyapi.sh status   # Container und Auth-Dateien
./hosting/cliproxyapi/cliproxyapi.sh test     # 401 ohne/falscher Key, Modellliste mit Key
```

Ende-zu-Ende ueber Open WebUI (Streaming, lange Historie, parallele Sitzungen,
Tool-Zyklus, Titel): `webui_e2e.py` in den Container kopieren und mit `PW` aus
`/root/.open-webui-admin-password` starten. Verbraucht etwas Kontingent.

## Neu anmelden

Die Login-Commands starten einen kurzlebigen Container `cliproxyapi-login`, Callback-Ports
nur auf `127.0.0.1`. Ohne SSH-Tunnel vom Betreiber-PC: Die Callback-URL laedt im Browser
nicht; sie wird dann auf `tposylka` per `curl 'http://127.0.0.1:<port>/…'` zugestellt.
Der Code ist einmalig und ohne PKCE-Verifier wertlos, trotzdem nicht in Logs ablegen.

1. ChatGPT-Grunddatei: `cliproxyapi.sh login-codex`, dann Geraetecode auf
   `https://auth.openai.com/codex/device` eingeben.
2. SIWC binden: `cliproxyapi.sh siwc-bind <codex-datei.json>`, Link oeffnen, Callback
   auf Port 1455. Ohne Schritt 2 liefe ChatGPT ueber den Legacy-Codex-Weg.
3. Claude: `cliproxyapi.sh login-claude`, Callback auf Port 54545.
4. `cliproxyapi.sh login-stop`; `docker network rm cliproxyapi_login`.

## Sicherung und Rueckweg

- Gateway: `/backup/cliproxyapi/cliproxyapi-<zeit>.tar.gz` (0600, enthaelt Tokens und Key).
  Kein Timer; Tokens rotieren, Wiederherstellung ist im Zweifel ein neuer Login.
- WebUI-Verbindung vor der Aenderung: `/root/open-webui-openai-config-backup-20261026-154746.json`
  (OpenAI aus, nur Werkseintrag `api.openai.com` ohne Key).
- WebUI-Gesamtsicherung davor: `/backup/open-webui/open-webui-20261026-154627.tar.gz`.

Rueckweg: In Open WebUI unter Admin > Verbindungen die Gateway-Verbindung deaktivieren
oder `webui_connect.py`-Muster mit dem gesicherten Stand an `/openai/config/update`
schicken; danach `docker compose -f /opt/docker/cliproxyapi/compose.yaml stop`.
Volumes und WebUI-Daten bleiben. Kein Datenbank-Restore ohne Abstimmung.

## Grenzen

- SIWC ist laut OpenAI ein Preview fuer persoenliche Nutzung; Konto-Sharing und das
  Weiterleiten von Claude-Abo-Logins widersprechen den Anbieterbedingungen. Auf
  ausdruecklichen Wunsch des Betreibers trotzdem eingerichtet; Sperrrisiko liegt beim Konto.
- Ob Anthropic die Gateway-Nutzung im Abo oder als Extra-Nutzung abrechnet, zeigt nur
  das Claude-Konto.
- Planlimits und 429 werden ohne Wiederholung an Open WebUI durchgereicht. Ein echtes
  Limit, Token-Widerruf und SIWC-Refresh (Token 1 h gueltig) wurden bei der Einrichtung
  noch nicht beobachtet.
- Die Compose-ENV von Open WebUI sagt weiter `ENABLE_OPENAI_API: "false"`. Massgeblich
  ist die persistente Einstellung in der Datenbank (`openai.enable = true`).
