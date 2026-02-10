#!/bin/sh
set -e

echo "Waiting for Postgres..."

# Wait until Postgres is ready
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Postgres not ready..."
  sleep 2
done

echo "Postgres ready"

# Run migrations only if MIGRATE_DB=true
if [ "$MIGRATE_DB" = "true" ] && [ "$SERVICE_TYPE" = "web" ]; then
  echo "Running database migrations..."
  python manage.py collectstatic --noinput --clear
  python manage.py migrate --noinput
else
  echo "Skipping database migrations"
fi

# Load bashrc if it exists
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi

# Finally start CMD
exec "$@"
