#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-${REPO_ROOT}/mariadb_backup_folder}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
COMPOSE_SERVICE="${COMPOSE_SERVICE:-mariadb}"
ENV_FILE="${COMPOSE_ENV_FILE:-${REPO_ROOT}/.env}"
COMPOSE_FILE_ARGS=()
COMPOSE_ENV_ARGS=()
TMP_FILE=""

log() {
  printf '[mariadb-backup] %s\n' "$*"
}

fail() {
  printf '[mariadb-backup] ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<USAGE
Usage: ./scripts/daily-mariadb-backup.sh [--env local|production]

Creates a compressed MariaDB dump from the Docker Compose service named
"mariadb" by default and stores it in mariadb_backup_folder.

Options:
  --env VALUE  Deployment mode: local or production. Defaults to DEPLOY_ENV or local.
  -h, --help   Show this help.

Environment overrides:
  BACKUP_DIR              Backup directory. Default: ${REPO_ROOT}/mariadb_backup_folder
  BACKUP_RETENTION_DAYS   Days to retain backups. Default: 14. Set to 0 to disable pruning.
  COMPOSE_SERVICE         Compose service to exec into. Default: mariadb.
  DEPLOY_ENV              Compose mode: local or production. Default: local.
  COMPOSE_ENV_FILE        Env file passed to Compose when present. Default: ${REPO_ROOT}/.env

Examples:
  ./scripts/daily-mariadb-backup.sh
  DEPLOY_ENV=production ./scripts/daily-mariadb-backup.sh
  BACKUP_DIR=/srv/backups/webapi-mariadb ./scripts/daily-mariadb-backup.sh
  BACKUP_RETENTION_DAYS=0 ./scripts/daily-mariadb-backup.sh

Cron example for daily 2:00 AM execution:
  0 2 * * * cd ${REPO_ROOT} && ${REPO_ROOT}/scripts/daily-mariadb-backup.sh >> ${REPO_ROOT}/mariadb_backup_folder/backup.log 2>&1
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      [[ $# -ge 2 ]] || fail "--env requires a value"
      [[ "$2" == "local" || "$2" == "production" ]] || fail "--env must be local or production"
      DEPLOY_ENV="$2"
      export DEPLOY_ENV
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

cleanup() {
  if [[ -n "${TMP_FILE}" && -f "${TMP_FILE}" ]]; then
    rm -f "${TMP_FILE}"
  fi
}
trap cleanup EXIT

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
  "${COMPOSE_CMD[@]}" "${COMPOSE_FILE_ARGS[@]}" "${COMPOSE_ENV_ARGS[@]}" "$@"
}

configure_deploy_env() {
  DEPLOY_ENV="${DEPLOY_ENV:-local}"

  case "${DEPLOY_ENV}" in
    local)
      COMPOSE_FILE_ARGS=(-f docker-compose.yml -f docker-compose.local.yml)
      ;;
    production)
      COMPOSE_FILE_ARGS=(-f docker-compose.yml -f docker-compose.prod.yml)
      ;;
    *)
      fail "DEPLOY_ENV must be local or production, got: ${DEPLOY_ENV}"
      ;;
  esac

  export DEPLOY_ENV
}

configure_env_file() {
  if [[ -f "${ENV_FILE}" ]]; then
    COMPOSE_ENV_ARGS=(--env-file "${ENV_FILE}")
  fi
}

validate_retention() {
  [[ "${BACKUP_RETENTION_DAYS}" =~ ^[0-9]+$ ]] || fail "BACKUP_RETENTION_DAYS must be a non-negative integer"
}

create_backup_dir() {
  mkdir -p "${BACKUP_DIR}" || fail "Could not create backup directory: ${BACKUP_DIR}"
  [[ -d "${BACKUP_DIR}" ]] || fail "Backup path is not a directory: ${BACKUP_DIR}"
}

run_backup() {
  local backup_file filename size timestamp

  timestamp="$(date +%Y%m%d-%H%M%S)"
  filename="mariadb-all-${timestamp}.sql.gz"
  backup_file="${BACKUP_DIR}/${filename}"
  TMP_FILE="${BACKUP_DIR}/.${filename}.tmp"

  log "Writing backup to ${backup_file}..."
  if ! compose exec -T "${COMPOSE_SERVICE}" sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" mariadb-dump --all-databases --single-transaction --quick --routines --events --triggers --hex-blob -u root' \
    | gzip -c > "${TMP_FILE}"; then
    fail "MariaDB dump failed. Ensure the Compose service '${COMPOSE_SERVICE}' is running and root credentials are configured."
  fi

  [[ -s "${TMP_FILE}" ]] || fail "Backup output is empty: ${TMP_FILE}"
  gzip -t "${TMP_FILE}" || fail "Backup gzip integrity check failed: ${TMP_FILE}"
  mv "${TMP_FILE}" "${backup_file}" || fail "Could not move backup into place: ${backup_file}"
  TMP_FILE=""

  [[ -s "${backup_file}" ]] || fail "Final backup file is missing or empty: ${backup_file}"
  size="$(du -h "${backup_file}" | cut -f1)"
  log "Backup completed: ${backup_file} (${size})"
}

prune_old_backups() {
  if [[ "${BACKUP_RETENTION_DAYS}" == "0" ]]; then
    log "Retention pruning disabled."
    return
  fi

  log "Pruning mariadb-all-*.sql.gz backups older than ${BACKUP_RETENTION_DAYS} days in ${BACKUP_DIR}..."
  find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'mariadb-all-*.sql.gz' -mtime +"${BACKUP_RETENTION_DAYS}" -print -delete
}

cd "${REPO_ROOT}"
detect_compose
configure_deploy_env
configure_env_file
validate_retention
create_backup_dir
run_backup
prune_old_backups
