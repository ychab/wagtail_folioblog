.DEFAULT_GOAL := help
.PHONY: help
.EXPORT_ALL_VARIABLES:

CURRENT_MAKEFILE := $(lastword $(MAKEFILE_LIST))
FIXTURES_FILE_ID = 11smbQZPF-wib-aMRUgR_uPuBzR_7zd1t

include .env

help:
	@LC_ALL=C $(MAKE) -pRrq -f $(CURRENT_MAKEFILE) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

confirm:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]

################
# Local command
################

deps:
	poetry show --outdated
	npm outdated

poetry:
	poetry update
	poetry lock
	poetry export -f requirements.txt --with prod -o requirements/prod.txt
	poetry export -f requirements.txt --with test -o requirements/test.txt
	poetry export -f requirements.txt --with test,dev -o requirements/dev.txt

npm:
	npm update
	npm run dist

precommit:
	pre-commit autoupdate

trans:
	cd folioblog && python ../manage.py makemessages -d django -l en -l es -l fr
	cd folioblog && python ../manage.py makemessages -d djangojs -l en -l es -l fr
	cd folioblog && python ../manage.py compilemessages -l en -l es -l fr

fixtures_dump:
	python manage.py fixtures dump
	@# We don't want to import/export revisions!
	sed -i -E 's/"latest_revision_created_at": (.+)/"latest_revision_created_at": null,/g' folioblog/core/fixtures/pages.json
	sed -i -E 's/"live_revision": (.+)/"live_revision": null,/g' folioblog/core/fixtures/pages.json
	sed -i -E 's/"latest_revision": (.+)/"latest_revision": null,/g' folioblog/core/fixtures/pages.json

fixtures_load:
	python manage.py fixtures load --reset

################
# Docker command
################

ps:
	docker compose ps --all

build:
	docker compose build app

rebuild:
	docker compose build --no-cache app

up:
	docker compose up -d

up_wait:
	FOLIOBLOG_HEALTHCHECK_INTERVAL=5s FOLIOBLOG_HEALTHCHECK_RETRIES=10 docker compose up --detach --wait

down:
	docker compose down --remove-orphans

down_clean:
	docker compose down --volumes --remove-orphans --rmi local

restart:
	docker compose restart

prune: confirm
	@# Be CAREFUL, would removed ALL unused stuff on your local machine!
	@# Be sure to have all your compose services RUNNING before execting it!
	docker system prune --all --force --volumes

reload: down up
reset: down_clean up

##############
# Docker utils
##############

dbshell:
	docker compose exec postgres psql -U ${FOLIOBLOG_POSTGRES_USER} -d ${FOLIOBLOG_POSTGRES_DB}

redisshell:
	docker compose exec redis redis-cli --user ${FOLIOBLOG_REDIS_USER} -a ${FOLIOBLOG_REDIS_PASSWORD}

redisflush:
	docker compose exec redis redis-cli --user ${FOLIOBLOG_REDIS_USER} -a ${FOLIOBLOG_REDIS_PASSWORD} flushall

nginxshell:
	docker compose exec nginx /bin/bash

appshell:
	docker compose run --rm app /bin/bash

appshellroot:
	docker compose run --rm --user=root app /bin/bash

applogs:
	docker compose logs -f app

appdeps:
	docker compose run --rm app bash -c 'poetry show --outdated; npm outdated'

apppoetry:
	@# Don't update packages while Python processes are still running so run another container!
	docker compose run --rm app bash -c '\
		poetry update; \
		poetry lock; \
		poetry export -f requirements.txt --with prod -o requirements/prod.txt; \
		poetry export -f requirements.txt --with test -o requirements/test.txt; \
		poetry export -f requirements.txt --with test,dev -o requirements/dev.txt;'

appnpm:
	docker compose run --rm app bash -c 'npm update; npm run dist'

appadmin:
	docker compose run --rm app python manage.py createadmin --username=${FOLIOBLOG_ADMIN_USERNAME} --password=${FOLIOBLOG_ADMIN_PASSWD}

appmigrate:
	docker compose run --rm app python manage.py migrate --noinput

apptrans:
	docker compose run --rm app bash -c 'cd folioblog && python ../manage.py makemessages -d django -l en -l es -l fr'
	docker compose run --rm app bash -c 'cd folioblog && python ../manage.py makemessages -d djangojs -l en -l es -l fr'
	docker compose run --rm app bash -c 'cd folioblog && python ../manage.py compilemessages -l en -l es -l fr'

appfixturesdump:
	docker compose run --rm app python manage.py fixtures dump
	sed -i -E 's/"latest_revision_created_at": (.+)/"latest_revision_created_at": null,/g' folioblog/core/fixtures/pages.json
	sed -i -E 's/"live_revision": (.+)/"live_revision": null,/g' folioblog/core/fixtures/pages.json
	sed -i -E 's/"latest_revision": (.+)/"latest_revision": null,/g' folioblog/core/fixtures/pages.json

appfixturesload:
	docker compose run --rm app python manage.py fixtures load --reset

apptest:
	docker compose run --rm app bash -c 'DJANGO_SETTINGS_MODULE=folioblog.settings.test python manage.py test --noinput --exclude-tag=slow --parallel=4 folioblog'

apptox:
	docker compose run --rm app tox

appcron:
	docker compose run --rm app python manage.py fixtree --full
	docker compose run --rm app python manage.py purge_revisions --days=30
	docker compose run --rm app python manage.py publish_scheduled_pages
	docker compose run --rm app python manage.py generaterenditions

##############
# Initial data
##############

initial_media:
	rm -Rf media/favicons media/images media/original_images
	wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=${FIXTURES_FILE_ID}' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=${FIXTURES_FILE_ID}" -O media.tar.gz && rm -rf /tmp/cookies.txt
	tar xzf media.tar.gz
	rm media.tar.gz

initial_data: initial_media fixtures_load

initial_data_dev: initial_media appfixturesload

initial_data_prod: initial_media appfixturesload
	docker compose cp media/. app:/app/media
	docker compose exec app python manage.py updatesite --site=1 --hostname=folio.local --port 443

#############
# Certificate
#############

certs:
	openssl req -x509 \
		-nodes \
		-days 365 \
		-newkey rsa:2048 \
		-keyout ./docker/prod/nginx/ssl/certs/folio-selfsigned.key \
		-out ./docker/prod/nginx/ssl/certs/folio-selfsigned.crt \
		-config ./docker/prod/nginx/ssl/csr.conf

###############
# Restore tools
###############

restore_media:
	scp ${FOLIOBLOG_BACKUP_HOST}:${FOLIOBLOG_BACKUP_PATH_MEDIA}/*.tgz .
	mv media media_old
	mv *.tgz latest.tar.gz
	tar xzf latest.tar.gz
	rm -Rf media_old latest.tar.gz

restore_db:
	# First drop the DB
	docker compose down --volumes
	# Then recreate the DB (and wait for it's ready!)
	FOLIOBLOG_HEALTHCHECK_INTERVAL=5s FOLIOBLOG_HEALTHCHECK_RETRIES=10 docker compose up --detach --wait
	# Then fetch remote backup and restore it.
	scp ${FOLIOBLOG_BACKUP_HOST}:${FOLIOBLOG_BACKUP_PATH_SQL}/*.sql.gz ./dump.sql.gz
	gunzip < dump.sql.gz | docker compose exec --no-TTY postgres psql --quiet -U ${FOLIOBLOG_POSTGRES_USER} -d ${FOLIOBLOG_POSTGRES_DB}
	# Finally cleanup the room!
	rm -f dump.sql.gz

restore_local: restore_media restore_db
	python manage.py createadmin --password=admin
	python manage.py updatesite --site=1 --hostname=folio.local --port 8000
	python manage.py updatesite --site=2 --hostname=blog.folio.local --port 8000
	python manage.py updatesite --site=3 --hostname=demo.folio.local --port 8000

restore_dev: restore_media restore_db
	docker compose exec app python manage.py createadmin --password=admin
	docker compose exec app python manage.py updatesite --site=1 --hostname=folio.local --port 8000
	docker compose exec app python manage.py updatesite --site=2 --hostname=blog.folio.local --port 8000
	docker compose exec app python manage.py updatesite --site=3 --hostname=demo.folio.local --port 8000

restore_prod: restore_media restore_db
	docker compose cp media/. app:/app/media
	docker compose exec app python manage.py createadmin --username=${FOLIOBLOG_ADMIN_USERNAME} --password=${FOLIOBLOG_ADMIN_PASSWD}
	docker compose exec app python manage.py updatesite --site=1 --hostname=folio.local --port 443
	docker compose exec app python manage.py updatesite --site=2 --hostname=blog.folio.local --port 443
	docker compose exec app python manage.py updatesite --site=3 --hostname=demo.folio.local --port 443
