#!/usr/bin/env bash
set -e

echo "==> [1/4] Upgrading pip"
python -m pip install --upgrade pip

echo "==> [2/4] Installing Python dependencies from requirements.txt"
python -m pip install -r requirements.txt

echo "==> [3/4] Collecting static files"
python manage.py collectstatic --no-input

echo "==> [4/4] Running database migrations"
python manage.py migrate --no-input

echo "==> Build completed successfully"
