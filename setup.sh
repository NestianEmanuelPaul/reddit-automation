#!/usr/bin/env bash

# Oprim execuția dacă apare o eroare
set -e

# echo "🔹 Creare mediu virtual..."
# python3 -m venv .venv

# echo "🔹 Activare mediu virtual..."
# source .venv/bin/activate

echo "🔹 Instalare dependențe..."
pip install --upgrade pip
pip install -r requirements.txt
pip freeze > requirements.txt

echo "🔹 Pornire server FastAPI..."
uvicorn app.main:app --reload
