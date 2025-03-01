#!/bin/sh
set -e

echo "Waiting for database..."
while ! mysqladmin ping -h"$DB_HOST" --silent; do
    sleep 1
done

echo "Running database migrations..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < ./schema.sql

echo "Starting application..."
exec python app.py
