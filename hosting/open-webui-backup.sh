#!/usr/bin/env bash
# Auf tposylka; konsistente SQLite-/Datei-Sicherung mit kurzer Schreibpause.
set -euo pipefail
umask 077

STACK=/opt/docker/open-webui
BACKUPS=/backup/open-webui
mkdir -p "$BACKUPS"
exec 9>"$BACKUPS/.lock"
flock -n 9 || exit 0
cd "$STACK"

if [[ $(docker inspect -f '{{.State.Running}}' open-webui) != true ]]; then
    echo 'Open WebUI laeuft nicht; keine automatische Sicherung.' >&2
    exit 1
fi

restart_needed=1
cleanup() {
    if [[ $restart_needed == 1 ]]; then
        docker compose start open-webui
    fi
}
trap cleanup EXIT
docker compose stop -t 60 open-webui

archive="$BACKUPS/open-webui-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$archive.partial" -C "$STACK" compose.yaml .env data \
    -C /var/www/posylka.de/.docker/nginx/etc/sites-enabled.test ai.colibo.io.conf
mv "$archive.partial" "$archive"
docker compose up -d --no-recreate --wait --wait-timeout 180 open-webui
restart_needed=0
trap - EXIT

find "$BACKUPS" -maxdepth 1 -type f -name 'open-webui-*.tar.gz' -mtime +14 -delete
printf 'Backup erstellt: %s\n' "$archive"
