#!/bin/sh
set -e

if [ "$1" = 'gunicorn' ]; then
  ADMIN_PASSWD="$(cat $FOLIOBLOG_ADMIN_PASSWD_FILE)"
  python manage.py migrate --noinput
  python manage.py createadmin --username=$FOLIOBLOG_ADMIN_USERNAME --password=$ADMIN_PASSWD
fi

exec "$@"
