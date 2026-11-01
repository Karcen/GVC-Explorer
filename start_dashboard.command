#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -f .venv/bin/activate ]; then
  echo 'First install: python3 -m venv .venv && source .venv/bin/activate && python -m pip install -e .'
  exit 1
fi
source .venv/bin/activate
exec streamlit run app.py
