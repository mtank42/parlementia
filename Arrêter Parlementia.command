#!/bin/bash
# Double-cliquez pour arrêter le serveur Parlementia.
DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$DIR/launcher/stop.sh"
