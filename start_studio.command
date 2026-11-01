#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -f .venv/.gvc_studio_020 ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -e .
  touch .venv/.gvc_studio_020
fi
exec .venv/bin/python desktop.py
