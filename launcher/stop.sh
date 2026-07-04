#!/bin/bash
# Arrête le serveur Parlementia.
PORT=8000
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PID="$(lsof -ti tcp:$PORT 2>/dev/null || true)"
if [ -n "$PID" ]; then
  kill $PID 2>/dev/null || true
  echo "Parlementia arrêté."
else
  echo "Aucun serveur Parlementia en cours."
fi
rm -f "$DIR/.cache/server.pid"
sleep 1
