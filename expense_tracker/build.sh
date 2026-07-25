#!/usr/bin/env bash
set -e

echo "==> [1/5] Upgrading pip"
python -m pip install --upgrade pip

echo "==> [2/5] Installing Python dependencies from requirements.txt"
python -m pip install -r requirements.txt

echo "==> [3/5] Collecting static files"
python manage.py collectstatic --no-input

echo "==> [4/5] Running database migrations"
python manage.py migrate --no-input

echo "==> [5/5] Configuring Site and Google SocialApp"
python manage.py configure_google_socialapp || echo "Skipped (tables may not exist yet)"

echo "==> Build completed successfully"
