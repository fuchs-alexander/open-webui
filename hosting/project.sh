#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
STACK=/opt/docker/open-webui
compose=(docker compose --project-directory "$STACK" -f "$HERE/compose.yaml")

case "${1:-check}" in
    check)
        "${compose[@]}" config --quiet
        "${compose[@]}" -f "$HERE/compose.source.yaml" config --quiet
        bash -n "$HERE/project.sh" "$HERE/open-webui-backup.sh"
        printf 'Compose, Source-Override und Shell-Syntax gueltig. Kein Build/Deploy ausgefuehrt.\n'
        ;;
    status)
        docker ps -a --filter 'name=^/open-webui$' \
            --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
        systemctl list-timers open-webui-backup.timer --no-pager
        ;;
    logs)
        docker logs --tail 100 open-webui
        ;;
    backup)
        systemctl start open-webui-backup.service
        systemctl show open-webui-backup.service --property=Result --property=ExecMainStatus
        ;;
    *)
        printf 'Aufruf: %s {check|status|logs|backup}\n' "$0" >&2
        exit 2
        ;;
esac
