# You must export these environment variables before using remote restore.
BACKUP_HOST=$(FOLIOBLOG_BACKUP_HOST)
BACKUP_PATH_SQL=$(FOLIOBLOG_BACKUP_PATH_SQL)
BACKUP_PATH_MEDIA=$(FOLIOBLOG_BACKUP_PATH_MEDIA)

all:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

help: all

check_deps:
	poetry show --outdated
	npm outdated

poetry:
	poetry update
	poetry lock
	poetry export -f requirements.txt --only main -o requirements/prod.txt
	poetry export -f requirements.txt --with test -o requirements/test.txt
	poetry export -f requirements.txt --with test,dev -o requirements/dev.txt

npm:
	npm update
	npm run dist

drop_db:
	psql -U postgres -c "DROP DATABASE folioblog"

create_db_user:
	psql -U postgres -c "CREATE USER folioblog WITH encrypted password 'folioblog' SUPERUSER"

create_db:
	psql -U postgres -c "CREATE DATABASE folioblog OWNER folioblog"

dump_db:
	pg_dump -U postgres -d folioblog > backup.sql

restore_db:
	scp ${BACKUP_HOST}:${BACKUP_PATH_SQL}/*.sql.gz .
	gunzip *.sql.gz
	mv *.sql latest.sql
	psql -U postgres -d folioblog < latest.sql
	python manage.py createadmin --password=admin --update
	python manage.py updatesite --hostname=127.0.0.1 --port 8000
	rm -f *.sql

restore_media:
	scp ${BACKUP_HOST}:${BACKUP_PATH_MEDIA}/*.tgz .
	mv media media_old
	mv *.tgz latest.tar.gz
	tar xvzf latest.tar.gz
	rm -Rf media_old latest.tar.gz

restore: drop_db create_db restore_db restore_media

migrate:
	python manage.py migrate

admin:
	python manage.py createadmin --password=admin

trans:
	cd folioblog && python ../manage.py makemessages -d django -l en -l fr
	cd folioblog && python ../manage.py makemessages -d djangojs -l en -l fr
	cd folioblog && python ../manage.py compilemessages -l en -l fr

fixtures_dump:
	python manage.py fixtures dump
	# We don't want to import/export revisions!
	sed -i -E 's/"latest_revision_created_at": (.+)/"latest_revision_created_at": null,/g' folioblog/core/fixtures/pages.json
	sed -i -E 's/"live_revision": (.+)/"live_revision": null,/g' folioblog/core/fixtures/pages.json
	sed -i -E 's/"latest_revision": (.+)/"latest_revision": null,/g' folioblog/core/fixtures/pages.json

fixtures_load:
	python manage.py fixtures load

reset: drop_db create_db migrate admin
