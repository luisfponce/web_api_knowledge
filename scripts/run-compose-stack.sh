#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMEOUT_SECONDS=120
BUILD_FLAG="--build"

log() {
  printf '[compose-stack] %s\n' "$*"
}

fail() {
  printf '[compose-stack] ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: ./scripts/run-compose-stack.sh [--no-build] [--timeout SECONDS]

Starts the MariaDB, backend, and frontend services with Docker Compose,
waits for readiness, and verifies minimum connectivity.

Options:
  --no-build          Start existing images without rebuilding them.
  --timeout SECONDS   Readiness timeout per check. Default: 120.
  -h, --help          Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-build)
      BUILD_FLAG=""
      shift
      ;;
    --timeout)
      [[ $# -ge 2 ]] || fail "--timeout requires a value"
      [[ "$2" =~ ^[0-9]+$ ]] || fail "--timeout must be a positive integer"
      TIMEOUT_SECONDS="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

detect_compose() {
  if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
    return
  fi

  if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
    return
  fi

  fail "Docker Compose is not available. Install the docker compose plugin or docker-compose."
}

compose() {
  "${COMPOSE_CMD[@]}" "$@"
}

wait_for_health() {
  local service="$1"
  local timeout="$2"
  local start_time now container_id status

  start_time="$(date +%s)"
  log "Waiting for ${service} health status..."

  while true; do
    container_id="$(compose ps -q "${service}" 2>/dev/null || true)"
    if [[ -n "${container_id}" ]]; then
      status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${container_id}" 2>/dev/null || true)"
      case "${status}" in
        healthy|running)
          log "${service} is ${status}."
          return 0
          ;;
        unhealthy|exited|dead)
          compose ps || true
          compose logs --tail=80 "${service}" || true
          fail "${service} became ${status}."
          ;;
      esac
    fi

    now="$(date +%s)"
    if (( now - start_time >= timeout )); then
      compose ps || true
      compose logs --tail=80 "${service}" || true
      fail "Timed out waiting for ${service} after ${timeout}s."
    fi

    sleep 3
  done
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local timeout="$3"
  local start_time now

  start_time="$(date +%s)"
  log "Checking ${name}: ${url}"

  while true; do
    if curl -fsS "${url}" >/dev/null; then
      log "${name} is reachable."
      return 0
    fi

    now="$(date +%s)"
    if (( now - start_time >= timeout )); then
      fail "Timed out waiting for ${name} at ${url}."
    fi

    sleep 3
  done
}

verify_api_proxy() {
  local url="http://127.0.0.1:8080/api/v1/auth/login"
  local status

  log "Checking nginx API proxy: ${url}"
  status="$(curl -sS -o /dev/null -w '%{http_code}' -X POST "${url}" -H 'Content-Type: application/json' -d '{}')"
  if [[ "${status}" == "422" ]]; then
    log "API proxy is reachable. FastAPI returned expected validation status 422."
    return 0
  fi

  fail "Expected HTTP 422 from proxied invalid login request, got HTTP ${status}."
}

verify_database() {
  log "Checking MariaDB connectivity inside the Compose service..."
  compose exec -T mariadb mariadb-admin ping -h 127.0.0.1 -u webapi_user -pwebapi_password >/dev/null
  log "MariaDB accepted ping."
}

docker_published_port_in_use() {
  local port="$1"
  local ports

  ports="$(docker ps --format '{{.Ports}}' 2>/dev/null || true)"
  [[ "${ports}" == *":${port}->"* ]]
}

configure_ports() {
  local candidate

  if [[ -z "${MARIADB_HOST_PORT:-}" ]] && docker_published_port_in_use 3306; then
    for candidate in 3307 3308 3309 3310 3311 3312 3313 3314 3315 3316 3317 3318 3319; do
      if ! docker_published_port_in_use "${candidate}"; then
        export MARIADB_HOST_PORT="${candidate}"
        log "Host port 3306 is already used by Docker; publishing Compose MariaDB on ${MARIADB_HOST_PORT} instead."
        return
      fi
    done

    fail "Host port 3306 is already used and no fallback MariaDB port from 3307-3319 is available."
  fi
}

start_stack() {
  if [[ -n "${BUILD_FLAG}" ]]; then
    log "Starting stack with image builds..."
    if compose up "${BUILD_FLAG}" -d; then
      return 0
    fi
  else
    log "Starting stack without rebuilding images..."
    if compose up -d; then
      return 0
    fi
  fi

  printf '\nDocker containers currently publishing ports:\n' >&2
  docker ps --format '  {{.Names}} {{.Ports}}' >&2 || true
  printf '\nIf port 3306, 8000, or 8080 is already used by an old webapi container, stop it first.\n' >&2
  printf 'Manual backend workflow cleanup example: docker rm -f webapi-mariadb webapi-backend\n' >&2
  printf 'Compose cleanup example: %s down\n' "${COMPOSE_CMD[*]}" >&2
  exit 1
}

detect_compose
configure_ports

cd "${REPO_ROOT}"

log "Using Compose command: ${COMPOSE_CMD[*]}"
start_stack

wait_for_health mariadb "${TIMEOUT_SECONDS}"
wait_for_health backend "${TIMEOUT_SECONDS}"
wait_for_http "frontend" "http://127.0.0.1:8080/" "${TIMEOUT_SECONDS}"
wait_for_http "backend direct endpoint" "http://127.0.0.1:8000/" "${TIMEOUT_SECONDS}"
verify_api_proxy
verify_database

log "Stack is ready."
printf '\nURLs:\n'
printf '  Frontend:               http://127.0.0.1:8080\n'
printf '  Backend direct:         http://127.0.0.1:8000\n'
printf '  Backend through nginx:  http://127.0.0.1:8080/api/v1/...\n'
printf '  MariaDB host port:      127.0.0.1:%s\n' "${MARIADB_HOST_PORT:-3306}"
printf '\nUseful commands:\n'
printf '  View services:  %s ps\n' "${COMPOSE_CMD[*]}"
printf '  View logs:      %s logs backend frontend mariadb\n' "${COMPOSE_CMD[*]}"
printf '  Stop stack:     %s down\n' "${COMPOSE_CMD[*]}"
printf '  Reset DB:       %s down -v\n' "${COMPOSE_CMD[*]}"
printf '  Get into DB container:  docker exec -ti $(docker ps -aqf "name=^/web_api_knowledge_mariadb*")  mariadb -u webapi_user -pwebapi_password \n'
