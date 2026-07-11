#!/usr/bin/env bash

# Launch the Metro Deep Dive research tool from any working directory.
# The script resolves the repo root from its own location, picks a known-good
# Python environment if one exists, and points Streamlit at the canonical
# DuckDB file used by the app.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
APP_PATH="${REPO_ROOT}/metro-deep-dive/research-tool/app.py"
DB_PATH_DEFAULT="${REPO_ROOT}/foundations/etl/data/duckdb/patterns_in_place.duckdb"

if [[ ! -f "${APP_PATH}" ]]; then
  echo "Research tool app not found at ${APP_PATH}" >&2
  exit 1
fi

# Prefer environments that can actually import Streamlit, not just ones that exist.
choose_python() {
  local candidate
  for candidate in \
    "${REPO_ROOT}/area-explorer/.venv/bin/python" \
    "${REPO_ROOT}/.venv312/bin/python" \
    "${REPO_ROOT}/.venv/bin/python" \
    "python3"
  do
    if [[ "${candidate}" == "python3" ]]; then
      if command -v python3 >/dev/null 2>&1 && python3 -c "import streamlit" >/dev/null 2>&1; then
        echo "python3"
        return 0
      fi
    elif [[ -x "${candidate}" ]] && "${candidate}" -c "import streamlit" >/dev/null 2>&1; then
      echo "${candidate}"
      return 0
    fi
  done

  return 1
}

if ! PYTHON_BIN="$(choose_python)"; then
  echo "No usable Python environment with Streamlit was found." >&2
  echo "Try installing dependencies into area-explorer/.venv or .venv312 first." >&2
  exit 1
fi

export DB_PATH="${DB_PATH:-${DB_PATH_DEFAULT}}"

cd "${REPO_ROOT}"
exec "${PYTHON_BIN}" -m streamlit run "${APP_PATH}" "$@"
