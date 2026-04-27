#!/usr/bin/env bash
# =============================================================================
# bootstrap-kener.sh — one-shot Kener configuration for the Mandari stack
# =============================================================================
# Idempotent: safe to run multiple times. Applies Mandari branding, replaces
# the default demo monitors, and (on first run) creates an API key the
# marketing website uses to pull live status data.
#
# Usage:
#     cd marketing-website
#     ./scripts/bootstrap-kener.sh
#
# Requires: docker, the Kener container running (`docker compose up -d kener`).
# =============================================================================
set -euo pipefail

KENER_CONTAINER="marketing-website-kener"
WEBSITE_CONTAINER="marketing-website"
COMPOSE_FILE="$(cd "$(dirname "$0")/.." && pwd)/docker-compose.yml"
ENV_FILE="$(cd "$(dirname "$0")/.." && pwd)/.env"
SCRIPT_LOCAL="$(cd "$(dirname "$0")" && pwd)/kener-bootstrap.mjs"
# Leading double-slash defeats Git Bash on Windows from rewriting the path
# from /tmp/... to C:\Users\...\AppData\Local\Temp\... when passed to docker.
SCRIPT_REMOTE="//tmp/kener-bootstrap.mjs"
SCRIPT_REMOTE_REAL="/tmp/kener-bootstrap.mjs"

C_GREEN='\033[0;32m'
C_YELLOW='\033[1;33m'
C_RED='\033[0;31m'
C_DIM='\033[2m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

step() { printf "${C_BOLD}==>${C_RESET} %s\n" "$1"; }
ok()   { printf "    ${C_GREEN}✓${C_RESET} %s\n" "$1"; }
warn() { printf "    ${C_YELLOW}⚠${C_RESET} %s\n" "$1"; }
fail() { printf "    ${C_RED}✗${C_RESET} %s\n" "$1" >&2; exit 1; }

# ─── Sanity checks ─────────────────────────────────────────────────────────
step "Pre-flight checks"
command -v docker >/dev/null 2>&1 || fail "docker not found in PATH"
docker inspect "$KENER_CONTAINER" >/dev/null 2>&1 || fail "Container $KENER_CONTAINER is not running. Start with: docker compose up -d"
[[ -f "$SCRIPT_LOCAL" ]] || fail "Bootstrap script not found at $SCRIPT_LOCAL"
ok "Container $KENER_CONTAINER is running"

# Wait until Kener is healthy (the script reads/writes the same SQLite file
# Kener uses, so we want it idle at startup completion)
printf "    Waiting for Kener to be healthy"
for i in {1..30}; do
    state=$(docker inspect "$KENER_CONTAINER" --format '{{.State.Health.Status}}' 2>/dev/null || echo "")
    if [[ "$state" == "healthy" ]]; then
        printf " ${C_GREEN}healthy${C_RESET}\n"
        break
    fi
    printf "."
    sleep 2
    [[ $i -eq 30 ]] && fail "Kener never reached healthy state"
done

# ─── Read KENER_SECRET_KEY from running container ─────────────────────────
step "Reading KENER_SECRET_KEY from container env"
KENER_SECRET_KEY=$(docker exec "$KENER_CONTAINER" sh -c 'echo "$KENER_SECRET_KEY"')
[[ -n "$KENER_SECRET_KEY" ]] || fail "KENER_SECRET_KEY is empty in container env"
ok "Got secret (length=${#KENER_SECRET_KEY})"

# ─── Run bootstrap (script piped in via stdin — avoids host-vs-container path issues) ───
step "Running bootstrap (logs to stderr, token on stdout)"
# Capture stdout (token) separately from stderr (progress logs).
TMP_STDOUT=$(mktemp)
docker exec -i -e "KENER_SECRET_KEY=$KENER_SECRET_KEY" "$KENER_CONTAINER" node - <"$SCRIPT_LOCAL" \
    > "$TMP_STDOUT" \
    2> >(sed 's/^/    /' >&2)
TOKEN=$(grep -oE 'KENER_API_TOKEN=[a-zA-Z0-9_]+' "$TMP_STDOUT" | head -1 | cut -d'=' -f2)
rm -f "$TMP_STDOUT"

if [[ -z "$TOKEN" ]]; then
    fail "Bootstrap did not return KENER_API_TOKEN — check output above"
fi

# ─── Update .env ──────────────────────────────────────────────────────────
step "Updating .env with API token"
if [[ "$TOKEN" == "__EXISTS__" ]]; then
    warn "API key already existed — token cannot be recovered."
    warn "If your .env doesn't have KENER_API_TOKEN set, delete the key in"
    warn "the Kener admin UI and re-run this script to generate a new one."
else
    [[ -f "$ENV_FILE" ]] || touch "$ENV_FILE"
    if grep -qE '^KENER_API_TOKEN=' "$ENV_FILE"; then
        # Replace existing line (portable sed across BSD/GNU)
        sed -i.bak -E "s|^KENER_API_TOKEN=.*|KENER_API_TOKEN=$TOKEN|" "$ENV_FILE" && rm -f "${ENV_FILE}.bak"
        ok "Updated KENER_API_TOKEN in $ENV_FILE"
    else
        printf "\nKENER_API_TOKEN=%s\n" "$TOKEN" >>"$ENV_FILE"
        ok "Appended KENER_API_TOKEN to $ENV_FILE"
    fi
fi

# ─── Restart Kener so the scheduler picks up new monitors ─────────────────
step "Restarting Kener so its scheduler picks up the new monitors"
docker restart "$KENER_CONTAINER" >/dev/null
ok "Kener restarted"

# ─── Restart marketing website to pick up new env (token) ─────────────────
if [[ "$TOKEN" != "__EXISTS__" ]] && docker inspect "$WEBSITE_CONTAINER" >/dev/null 2>&1; then
    step "Recreating marketing website container so it loads the new token"
    (cd "$(dirname "$COMPOSE_FILE")" && docker compose up -d website >/dev/null 2>&1)
    ok "Marketing website recreated"
fi

# ─── Done ─────────────────────────────────────────────────────────────────
printf "\n${C_BOLD}Done.${C_RESET}\n\n"
printf "  ${C_DIM}Status page (admin):${C_RESET}  http://localhost:6501/account/signin\n"
printf "  ${C_DIM}Status page (public):${C_RESET} http://localhost:6501/\n"
printf "  ${C_DIM}Marketing /status/:${C_RESET}   http://localhost:6500/status/\n\n"
printf "  ${C_DIM}First monitor checks run within 60 seconds (cron: every minute).${C_RESET}\n\n"
