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
if [ "$MIGRATE_DB" = "true" ]; then
  echo "Running database migrations..."
  python smallslive/manage.py collectstatic --noinput --clear
#  python smallslive/manage.py migrate order 0006_orderstatuschange --fake
#  python smallslive/manage.py migrate customer 0008_auto_20260207_0800 --fake
  python smallslive/manage.py migrate --noinput
else
  echo "Skipping database migrations"
fi

if [ "$RUN_MIGRATE_SCRIPT" = "true" ]; then
  echo "Running migrate.sh script..."
  bash /app/migrate.sh
else
  echo "Skipping migrate.sh script"
fi

# Finally start CMD
exec "$@"
