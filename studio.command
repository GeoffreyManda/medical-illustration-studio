#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -e '.[studio]'
fi
printf '\nOpen http://127.0.0.1:8765 in your browser. Press Ctrl+C to stop.\n\n'
exec .venv/bin/python -m medillustrate studio "$@"
