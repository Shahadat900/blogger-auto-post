#!/data/data/com.termux/files/usr/bin/bash

cd "$(dirname "$0")/.."

echo "============================================"
echo "  Islamic Guide - Local Run"
echo "  $(date)"
echo "============================================"

echo "[1/3] Pulling latest code..."
git pull origin main

echo "[2/3] Running auto poster..."
python scripts/main.py

echo "[3/3] Committing state changes..."
git add config.json posted_log.json
git diff --staged --quiet || git commit -m "auto: update posting state [skip ci]"
git push origin main

echo ""
echo "Done at $(date)"
