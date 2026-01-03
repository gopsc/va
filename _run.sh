#!/bin/bash
cd "$(dirname "$0")" || exit
bash ./_set.sh
source ./.env/bin/activate
exec python3 src/va.py
