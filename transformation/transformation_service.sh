#!/usr/bin/env bash
# transformation_service.sh
# Continuously checks every 1 minute for .parquet files anywhere under three dirs and runs `dbt run` when present.

set -euo pipefail

INTERVAL=30  # seconds (0.5 minute)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DBT_PROJECT_DIR="$(cd "${SCRIPT_DIR}" && pwd)"  # adjust if your dbt project lives elsewhere
DBT_CMD="dbt run"

OBS_DIR="${SCRIPT_DIR}/../ingestion_data/observations"
STATIONS_DIR="${SCRIPT_DIR}/../ingestion_data/stations"
ZONES_DIR="${SCRIPT_DIR}/../ingestion_data/zones"

# try to make paths absolute if they exist; otherwise warn and leave as-is (has_parquet will handle missing dirs)
if [ -d "${OBS_DIR}" ]; then OBS_DIR="$(cd "${OBS_DIR}" && pwd)"; else echo "Warning: ${OBS_DIR} does not exist yet"; fi
if [ -d "${STATIONS_DIR}" ]; then STATIONS_DIR="$(cd "${STATIONS_DIR}" && pwd)"; else echo "Warning: ${STATIONS_DIR} does not exist yet"; fi
if [ -d "${ZONES_DIR}" ]; then ZONES_DIR="$(cd "${ZONES_DIR}" && pwd)"; else echo "Warning: ${ZONES_DIR} does not exist yet"; fi

shopt -s nullglob

# return 0 if any .parquet file exists anywhere under the given directory (recursive), else return 1
has_parquet() {
    local dir="$1"
    [ -d "$dir" ] || return 1
    # find prints the first match then quits; grep -q checks for non-empty output
    if find "$dir" -type f -iname '*.parquet' -print -quit | grep -q .; then
        return 0
    else
        return 1
    fi
}

cleanup() {
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - exiting"
    exit 0
}
trap cleanup INT TERM

echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - transformation_service started, checking every ${INTERVAL}s"
while true; do
    if has_parquet "${OBS_DIR}" && has_parquet "${STATIONS_DIR}" && has_parquet "${ZONES_DIR}"; then
        echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - parquet files detected in all three directory trees; running: ${DBT_CMD}"
        (
            cd "${DBT_PROJECT_DIR}"
            if ${DBT_CMD}; then
                echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - dbt run completed successfully"
            else
                echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - dbt run failed" >&2
            fi
        )
    else
        echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") - waiting for parquet files in all three directory trees"
    fi
    sleep "${INTERVAL}"
done