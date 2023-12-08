#!/bin/sh
set -e

if [ ! -d /app/node_modules ]; then
    # Only once local source are mounted into the container, we could build sources.
    echo "Running NPM install"
    npm install
    npm run dist
fi

if [ "$3" = 'runserver' ]; then
    echo "Migrate database"
    python manage.py migrate --noinput
    python manage.py createadmin --username=admin --password=admin
fi

exec "$@"
