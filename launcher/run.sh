#!/bin/bash
# Lanceur Parlementia : prépare l'environnement, démarre le serveur et ouvre
# le navigateur. Appelé par Parlementia.app (double-clic) — sans console.
set -u

PORT=8000
# Dossier du projet = dossier parent de ce script (parlementia/).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$DIR/.venv"
PY="$VENV/bin/python"
UVICORN="$VENV/bin/uvicorn"
LOGDIR="$DIR/.cache"
mkdir -p "$LOGDIR"

cd "$DIR"

# 1. Environnement virtuel + dépendances (uniquement au 1er lancement).
if [ ! -x "$PY" ]; then
  /usr/bin/env python3 -m venv "$VENV" || exit 1
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q -r "$DIR/requirements.txt"
fi

# 2. Arrêter un serveur déjà présent sur le port (relance propre).
EXIST="$(lsof -ti tcp:$PORT 2>/dev/null || true)"
if [ -n "$EXIST" ]; then
  kill $EXIST 2>/dev/null || true
  sleep 1
fi

# 3. Démarrer le serveur en arrière-plan (détaché, logs dans .cache).
nohup "$UVICORN" server:app --host 127.0.0.1 --port "$PORT" --app-dir "$DIR" \
  > "$LOGDIR/server.log" 2>&1 &
echo $! > "$LOGDIR/server.pid"

# 4. Attendre que le serveur réponde (max ~20 s) puis ouvrir le navigateur.
for _ in $(seq 1 40); do
  if curl -s "http://127.0.0.1:$PORT/api/config" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

open "http://127.0.0.1:$PORT"
