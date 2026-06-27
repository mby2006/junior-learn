#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="${PYTHON_BIN:-python}"
VENV_DIR="${VENV_DIR:-venv}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-admin123}"

if [ ! -d "${VENV_DIR}" ]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if [ -x "${VENV_DIR}/Scripts/python.exe" ]; then
  VENV_PYTHON="${VENV_DIR}/Scripts/python.exe"
elif [ -x "${VENV_DIR}/bin/python" ]; then
  VENV_PYTHON="${VENV_DIR}/bin/python"
else
  VENV_PYTHON="${PYTHON_BIN}"
fi

"${VENV_PYTHON}" -m pip install --upgrade pip
"${VENV_PYTHON}" -m pip install -r requirements.txt
"${VENV_PYTHON}" -m pip install pydantic-settings

export BACKEND_PORT
export ADMIN_USER
export ADMIN_PASS

exec "${VENV_PYTHON}" src/api/run_server.py
