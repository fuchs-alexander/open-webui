#!/usr/bin/env bash
# CLIProxyAPI-Gateway fuer Open WebUI auf tposylka. Gibt nie Schluessel oder Tokens aus.
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
STACK=/opt/docker/cliproxyapi
# Betrieb immer mit der Live-Kopie; check validiert zusaetzlich die Vorlage hier.
compose=(docker compose --project-directory "$STACK" -f "$STACK/compose.yaml")

# Ruft das Gateway aus dem Open-WebUI-Container auf, also ueber denselben Weg wie
# das WebUI-Backend. Argumente: Pfad, Schluesselmodus (none|wrong|real).
probe() {
    local path=$1 mode=$2 key=''
    case "$mode" in
        wrong) key=invalid-test-key ;;
        real) key=$(sed -n 's/^    - "\(.*\)"$/\1/p' "$STACK/config.yaml" | head -n1) ;;
    esac
    docker exec -i -e PROBE_KEY="$key" -e PROBE_PATH="$path" open-webui python - <<'PY'
import json, os, urllib.request, urllib.error
req = urllib.request.Request("http://cliproxyapi:8317" + os.environ["PROBE_PATH"])
if os.environ["PROBE_KEY"]:
    req.add_header("Authorization", "Bearer " + os.environ["PROBE_KEY"])
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        body = json.load(r)
        ids = sorted(m.get("id", "?") + " (" + str(m.get("owned_by", "?")) + ")" for m in body.get("data", []))
        print(r.status, "models:", ", ".join(ids) if ids else "-")
except urllib.error.HTTPError as e:
    print(e.code)
PY
}

case "${1:-check}" in
    check)
        docker compose --project-directory "$STACK" -f "$HERE/compose.yaml" --profile login config --quiet
        "${compose[@]}" --profile login config --quiet
        cmp -s "$HERE/compose.yaml" "$STACK/compose.yaml" \
            || printf 'Hinweis: Vorlage und Live-compose.yaml unterscheiden sich.\n'
        bash -n "$HERE/cliproxyapi.sh"
        printf 'Compose und Shell-Syntax gueltig. Kein Start ausgefuehrt.\n'
        ;;
    status)
        docker ps -a --filter 'name=^/cliproxyapi' \
            --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
        ls -la "$STACK/auths" | awk 'NR>1 {print $1, $3, $NF}'
        ;;
    logs)
        docker logs --tail 100 cliproxyapi
        ;;
    test)
        printf 'ohne Schluessel:   '; probe /v1/models none
        printf 'falscher Schluessel: '; probe /v1/models wrong
        printf 'Gateway-Schluessel: '; probe /v1/models real
        ;;
    login-codex)
        # Geraetecode-Login fuer die gatewayeigene Codex-Grunddatei.
        "${compose[@]}" --profile login run -d --rm --name cliproxyapi-login login -codex-device-login
        printf 'Ausgabe: docker logs -f cliproxyapi-login\n'
        ;;
    siwc-bind)
        # Bindet SIWC an eine vorhandene Codex-Datei in auths/ (nur Dateiname).
        [[ -n ${2:-} ]] || { printf 'Aufruf: %s siwc-bind <codex-datei.json>\n' "$0" >&2; exit 2; }
        "${compose[@]}" --profile login run -d --rm --service-ports --name cliproxyapi-login login -siwc-bind "$2"
        printf 'Tunnel: ssh -N -L 1455:127.0.0.1:1455 root@tposylka\nAusgabe: docker logs -f cliproxyapi-login\n'
        ;;
    login-claude)
        "${compose[@]}" --profile login run -d --rm --service-ports --name cliproxyapi-login login -claude-login
        printf 'Tunnel: ssh -N -L 54545:127.0.0.1:54545 root@tposylka\nAusgabe: docker logs -f cliproxyapi-login\n'
        ;;
    login-stop)
        docker rm -f cliproxyapi-login >/dev/null 2>&1 || true
        printf 'Login-Container entfernt.\n'
        ;;
    *)
        printf 'Aufruf: %s {check|status|logs|test|login-codex|siwc-bind <datei>|login-claude|login-stop}\n' "$0" >&2
        exit 2
        ;;
esac
