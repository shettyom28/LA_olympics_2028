#!/bin/sh
set -e

cd /app

mkdir -p /app/storage/fileuploads /app/storage/objectstore

# ── 1. Always run migrations (safe to run multiple times) ─────────────────────
echo "[startup] Running database migrations..."
python manage.py migrate --no-input

# ── 2. Seed data if DB is empty (fresh install or after docker compose down -v)
echo "[startup] Checking for existing data..."
python manage.py shell -c "
from django.contrib.auth.models import User
from django.core.management import call_command

if not User.objects.exists():
    print('[startup] Empty database — loading seed data...')
    call_command('seeddata')
    print('[startup] Seed data loaded.')
else:
    print(f'[startup] Database already has {User.objects.count()} users — skipping seed.')
"

# ── 3. Always ensure demo account passwords are usable ────────────────────────
echo "[startup] Setting account passwords..."
python manage.py shell -c "
import os
from django.contrib.auth.models import User

accounts = {
    'admin':      os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin'),
    'staff1':     'staff123',
    'spectator1': 'spectator123',
}
for username, password in accounts.items():
    try:
        u = User.objects.get(username=username)
        u.set_password(password)
        u.is_active = True
        u.save(update_fields=['password', 'is_active'])
        print(f'  {username}: OK')
    except User.DoesNotExist:
        pass
"

# ── 4. Create/update service accounts from env vars ───────────────────────────
python manage.py create_service_accounts

# ── 5. Start server ───────────────────────────────────────────────────────────
echo "[startup] Starting server..."
exec opentelemetry-instrument gunicorn mysite.asgi:application \
    --worker-class asgi \
    --bind 0.0.0.0:8000 \
    --workers 4
