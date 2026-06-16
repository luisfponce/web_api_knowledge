#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMEOUT_SECONDS=120
BUILD_FLAG="--build"
ENV_FILE="${COMPOSE_ENV_FILE:-${REPO_ROOT}/.env}"
COMPOSE_ENV_ARGS=()
COMPOSE_PROJECT_ARGS=()
CLEAN_MODE="false"
RESET_DEFAULT="false"
PROJECT_NAME=""

log() {
  printf '[compose-stack] %s\n' "$*"
}

fail() {
  printf '[compose-stack] ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage: ./scripts/run-compose-stack.sh [--clean] [--project-name NAME] [--reset-default] [--no-build] [--timeout SECONDS]

Starts the MariaDB, Redis, backend, and frontend services with Docker Compose,
waits for readiness, and verifies minimum connectivity.

Options:
  --clean              Use an isolated Compose project and clean its containers/volumes before startup.
  --project-name NAME  Override Compose project name. Defaults to webapi_clean_<timestamp> with --clean.
  --reset-default      With --clean, also remove default project containers/volumes before startup.
  --no-build          Start existing images without rebuilding them.
  --timeout SECONDS   Readiness timeout per check. Default: 120.
  -h, --help          Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --clean)
      CLEAN_MODE="true"
      shift
      ;;
    --project-name)
      [[ $# -ge 2 ]] || fail "--project-name requires a value"
      [[ -n "$2" ]] || fail "--project-name must not be empty"
      PROJECT_NAME="$2"
      shift 2
      ;;
    --reset-default)
      RESET_DEFAULT="true"
      shift
      ;;
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
  "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}" "$@"
}

warn() {
  printf '[compose-stack] WARNING: %s\n' "$*" >&2
}

is_set() {
  local name="$1"
  [[ -n "${!name+x}" && -n "${!name}" ]]
}

load_env_file() {
  local line name value

  if [[ ! -f "${ENV_FILE}" ]]; then
    warn "No env file found at ${ENV_FILE}. Continuing with variables already exported in the shell. For local development, copy .env.example to .env and replace placeholder values."
    return
  fi

  COMPOSE_ENV_ARGS=(--env-file "${ENV_FILE}")
  log "Loading environment defaults from ${ENV_FILE}. Existing shell variables take precedence."

  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%$'\r'}"
    [[ -z "${line}" || "${line}" =~ ^[[:space:]]*# ]] && continue
    [[ "${line}" == export[[:space:]]* ]] && line="${line#export }"
    [[ "${line}" == *=* ]] || continue

    name="${line%%=*}"
    value="${line#*=}"
    name="${name//[[:space:]]/}"
    [[ "${name}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue

    if [[ ! -v "${name}" ]]; then
      value="${value%"${value##*[![:space:]]}"}"
      value="${value#"${value%%[![:space:]]*}"}"
      if [[ "${value}" == \"*\" && "${value}" == *\" ]]; then
        value="${value:1:${#value}-2}"
      elif [[ "${value}" == \'*\' && "${value}" == *\' ]]; then
        value="${value:1:${#value}-2}"
      fi
      export "${name}=${value}"
    fi
  done < "${ENV_FILE}"
}

configure_project_args() {
  if [[ -n "${PROJECT_NAME}" ]]; then
    COMPOSE_PROJECT_ARGS=(-p "${PROJECT_NAME}")
    return
  fi

  if [[ "${CLEAN_MODE}" == "true" ]]; then
    PROJECT_NAME="webapi_clean_$(date +%Y%m%d%H%M%S)"
    COMPOSE_PROJECT_ARGS=(-p "${PROJECT_NAME}")
  fi
}

reset_default_project() {
  if [[ "${RESET_DEFAULT}" != "true" ]]; then
    return
  fi

  if [[ "${CLEAN_MODE}" != "true" ]]; then
    fail "--reset-default requires --clean"
  fi

  log "Removing default Compose project containers and volumes..."
  "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" down --volumes --remove-orphans || true
}

clean_project_state() {
  if [[ "${CLEAN_MODE}" != "true" ]]; then
    return
  fi

  log "Cleaning isolated Compose project ${PROJECT_NAME} before startup..."
  compose down --volumes --remove-orphans || true
}

check_required_files() {
  local missing=()
  local required=(
    "${REPO_ROOT}/webapi/db/__init__.py"
    "${REPO_ROOT}/webapi/db/db_connection.py"
    "${REPO_ROOT}/webapi/db/redis_connection.py"
    "${REPO_ROOT}/frontend/nginx.conf"
    "${REPO_ROOT}/Dockerfile"
    "${REPO_ROOT}/frontend/Dockerfile"
  )
  local path

  for path in "${required[@]}"; do
    [[ -f "${path}" ]] || missing+=("${path}")
  done

  if (( ${#missing[@]} > 0 )); then
    printf '[compose-stack] ERROR: Missing required files:\n' >&2
    printf '  %s\n' "${missing[@]}" >&2
    exit 1
  fi
}

check_environment() {
  local missing=()
  local placeholder=()
  local important_vars=(
    MARIADB_ROOT_PASSWORD
    MARIADB_PASSWORD
    DB_URL
    ENV_MAIL_PASSWORD
    ENV_SECRET_KEY
  )
  local recommended_vars=(
    MARIADB_DATABASE
    MARIADB_USER
    REDIS_HOST
    REDIS_PORT
    ENV_MAIL_USERNAME
    ENV_MAIL_FROM
  )
  local var

  for var in "${important_vars[@]}"; do
    if ! is_set "${var}"; then
      missing+=("${var}")
    fi
  done

  if (( ${#missing[@]} > 0 )); then
    warn "Missing important environment variables: ${missing[*]}. Compose/application defaults will be used so deployment can continue."
    warn "Components affected: MariaDB credentials use local placeholders when MARIADB_ROOT_PASSWORD or MARIADB_PASSWORD is missing; backend DB/JWT behavior depends on DB_URL and ENV_SECRET_KEY; SMTP mail services may fail or remain test-only when ENV_MAIL_PASSWORD is missing."
    warn "Recommended setup: keep these keys in .env for local runs, inject them from platform secrets in production, and define them as CI/CD secrets for pipeline jobs that need the backend."
  fi

  for var in "${recommended_vars[@]}"; do
    if ! is_set "${var}"; then
      warn "${var} is not set; Compose/application defaults will be used where available."
    fi
  done

  for var in "${important_vars[@]}" "${recommended_vars[@]}"; do
    if is_set "${var}" && [[ "${!var}" == replace_with_* ]]; then
      placeholder+=("${var}")
    fi
  done

  if (( ${#placeholder[@]} > 0 )); then
    warn "Placeholder values detected for: ${placeholder[*]}. This is acceptable only for isolated local or test runs. Replace them for shared, staging, or production deployments."
  fi

  if is_set DB_URL && [[ "${DB_URL}" != mariadb+mariadbconnector://* ]]; then
    warn "DB_URL does not use the expected MariaDB connector prefix. The backend may use another database target; verify this is intentional for the current environment."
  fi

  if [[ "${ENV_MAIL_USERNAME:-}" == "test@example.com" || "${ENV_MAIL_FROM:-}" == "test@example.com" || "${ENV_MAIL_PASSWORD:-}" == replace_with_* || -z "${ENV_MAIL_PASSWORD:-}" ]]; then
    warn "SMTP mail services may not send real email with test or placeholder ENV_MAIL_* values. Authentication, CRUD, and local stack health can still work if outbound email is not required."
  fi

  log "Environment configuration check completed."
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
  compose exec -T mariadb sh -c 'MYSQL_PWD="$MARIADB_PASSWORD" mariadb-admin ping -h 127.0.0.1 -u "$MARIADB_USER" >/dev/null'
  log "MariaDB accepted ping."
}

verify_redis() {
  local response

  log "Checking Redis connectivity inside the Compose service..."
  response="$(compose exec -T redis redis-cli ping)"
  [[ "${response}" == "PONG" ]] || fail "Expected Redis PONG, got: ${response}"
  log "Redis accepted ping."
}

docker_published_port_in_use() {
  local port="$1"
  local ports

  ports="$(docker ps --format '{{.Ports}}' 2>/dev/null || true)"
  [[ "${ports}" == *":${port}->"* ]]
}

configure_ports() {
  local candidate

  if [[ "${CLEAN_MODE}" == "true" ]]; then
    if [[ -z "${MARIADB_HOST_PORT:-}" ]] && docker_published_port_in_use 3306; then
      fail "Host port 3306 is already used. Stop the conflicting container or rerun with MARIADB_HOST_PORT=<free-port>."
    fi

    if [[ -z "${REDIS_HOST_PORT:-}" ]] && docker_published_port_in_use 6379; then
      fail "Host port 6379 is already used. Stop the conflicting container or rerun with REDIS_HOST_PORT=<free-port>."
    fi

    if docker_published_port_in_use 8000; then
      fail "Host port 8000 is already used. docker-compose.yml hardcodes backend port 8000, so stop the conflicting container before clean startup."
    fi

    if docker_published_port_in_use 8080; then
      fail "Host port 8080 is already used. docker-compose.yml hardcodes frontend port 8080, so stop the conflicting container before clean startup."
    fi

    return
  fi

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
  if [[ "${CLEAN_MODE}" == "true" ]]; then
    printf '\nIf legacy docker-compose hit the ContainerConfig recreate bug, remove only containers for this project and retry:\n' >&2
    printf "  docker ps -a --format '{{.Names}}' | grep '%s' | xargs -r docker rm -f\n" "${PROJECT_NAME}" >&2
    if [[ -n "${BUILD_FLAG}" ]]; then
      printf "  %s -p '%s' up %s -d\n" "${COMPOSE_CMD[*]}" "${PROJECT_NAME}" "${BUILD_FLAG}" >&2
    else
      printf "  %s -p '%s' up -d\n" "${COMPOSE_CMD[*]}" "${PROJECT_NAME}" >&2
    fi
    printf 'Clean project teardown: %s down --volumes --remove-orphans\n' "$(printf '%q ' "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}")" >&2
  else
    printf '\nIf port 3306, 6379, 8000, or 8080 is already used by an old webapi container, stop it first.\n' >&2
    printf 'Manual backend workflow cleanup example: docker rm -f webapi-mariadb webapi-redis webapi-backend\n' >&2
  fi
  if [[ -n "${BUILD_FLAG}" ]]; then
    printf 'Redis port override example: REDIS_HOST_PORT=6380 %s up %s -d\n' "${COMPOSE_CMD[*]}" "${BUILD_FLAG}" >&2
  else
    printf 'Redis port override example: REDIS_HOST_PORT=6380 %s up -d\n' "${COMPOSE_CMD[*]}" >&2
  fi
  printf 'Compose cleanup example: %s down\n' "${COMPOSE_CMD[*]}" >&2
  exit 1
}

cd "${REPO_ROOT}"

detect_compose
load_env_file
configure_project_args
check_required_files
check_environment
reset_default_project
clean_project_state
configure_ports

log "Using Compose command: ${COMPOSE_CMD[*]}"
if [[ "${CLEAN_MODE}" == "true" ]]; then
  log "Using isolated Compose project: ${PROJECT_NAME}"
fi
start_stack

wait_for_health mariadb "${TIMEOUT_SECONDS}"
wait_for_health redis "${TIMEOUT_SECONDS}"
wait_for_health backend "${TIMEOUT_SECONDS}"
wait_for_http "frontend" "http://127.0.0.1:8080/" "${TIMEOUT_SECONDS}"
wait_for_http "backend direct endpoint" "http://127.0.0.1:8000/" "${TIMEOUT_SECONDS}"
verify_api_proxy
verify_database
verify_redis

log "Stack is ready."
printf '\nURLs:\n'
printf '  Frontend:               http://127.0.0.1:8080\n'
printf '  Backend direct:         http://127.0.0.1:8000/docs\n'
printf '  Backend through nginx:  http://127.0.0.1:8080/api/v1/...\n'
printf '  MariaDB host port:      127.0.0.1:%s\n' "${MARIADB_HOST_PORT:-3306}"
printf '  Redis host port:        127.0.0.1:%s\n' "${REDIS_HOST_PORT:-6379}"
printf '\nUseful commands:\n'
printf '  View services:  %s ps\n' "$(printf '%q ' "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}")"
printf '  View logs:      %s logs backend frontend mariadb redis\n' "$(printf '%q ' "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}")"
printf '  Check Redis:    %s exec redis redis-cli ping\n' "$(printf '%q ' "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}")"
printf '  Stop stack:     %s down\n' "$(printf '%q ' "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}")"
printf '  Reset DB:       %s down -v\n' "$(printf '%q ' "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}")"
printf '  Get into DB container:  %s exec mariadb sh -c '\''MYSQL_PWD="$MARIADB_PASSWORD" mariadb "$MARIADB_DATABASE" -u "$MARIADB_USER"'\''\n' "$(printf '%q ' "${COMPOSE_CMD[@]}" "${COMPOSE_ENV_ARGS[@]}" "${COMPOSE_PROJECT_ARGS[@]}")"
