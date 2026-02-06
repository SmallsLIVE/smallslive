#!/bin/sh

set -e

echo "Waiting for postgres..."

until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Postgres not ready..."
  sleep 2
done

echo "Postgres ready"

python manage.py collectstatic --noinput --clear
python manage.py migrate --noinput

exec "$@"
