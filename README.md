[![DockerHub](https://github.com/ychab/wagtail_folioblog/actions/workflows/dockerhub.yaml/badge.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/dockerhub.yaml)
[![build](https://github.com/ychab/wagtail_folioblog/actions/workflows/build.yaml/badge.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/build.yaml)
[![lint](https://github.com/ychab/wagtail_folioblog/actions/workflows/lint.yaml/badge.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/lint.yaml)
[![units](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/units.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/units.yaml)
[![end2end](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/selenium.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/selenium.yaml)
[![poetry](https://github.com/ychab/wagtail_folioblog/actions/workflows/poetry.yaml/badge.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/poetry.yaml)
[![NPM deps](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/npm-dependencies.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/npm.yaml)
[![wagtail version](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/poetry-wagtail-version.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/version.yaml)

# FolioBlog, a Wagtail portfolio / blog demo

The FolioBlog project is the combination of a portfolio and blogs, with a
**multi-tenancy** + **multi-language** context, build with the powerful Wagtail CMS.

It's main goal is to be a showcase for best practices integrations with:

Backend:
* [Django Web Framework](https://www.djangoproject.com/)
* [Wagtail CMS](https://wagtail.org/)

Frontend (Vanilla JS, please):
* [Bootstrap 5.1](https://getbootstrap.com/docs/5.1/)
* [Fontawesome](https://fontawesome.com/)
* [Packery](https://packery.metafizzy.co/)
* [Flickity](https://flickity.metafizzy.co/)
* [Infinite scroll](https://infinite-scroll.com/)
* [AutocompleJS](https://tarekraafat.github.io/autoComplete.js/)
* [Tagify](https://yaireo.github.io/tagify/)
* [GLightbox](https://biati-digital.github.io/glightbox/)

Database:
* [PostgreSQL](https://www.postgresql.org/)
* [Redis](https://redis.com/) (cache)

Testing:
* Units and functionals:
  * [Coverage](https://coverage.readthedocs.io/en/latest/)
  * [Factory Boy](https://factoryboy.readthedocs.io/en/latest/) and [Wagtail Factories](https://wagtail-factories.readthedocs.io/en/latest/)
* End to end (integration:
  * [Selenium](https://www.selenium.dev/)

Coding style:
* [Black](https://black.readthedocs.io/en/stable/index.html)
* [Pylama](https://github.com/klen/pylama)
* [isort](https://pycqa.github.io/isort/)
* [djhtml](https://github.com/rtts/djhtml)

Integration / Automation:
* [Tox](https://tox.wiki/en/latest/)
* [Pre-commit](https://pre-commit.com/)
* [GitHub Action](https://github.com/features/actions)
* [Docker](https://www.docker.com/)
* [Docker compose](https://docs.docker.com/compose/)

## Setup

You can set up this project in multiple ways:
* Local only: All services and Python code are on your local machine
* Docker local: with Docker services, but keep Python app on your local machine
* Docker dev: with Docker services, including a dev app container
* Docker prod: with Docker services, but more close from production (gunicorn, nginx)

If you plan to use [Docker compose](https://docs.docker.com/compose/install/),
you **must** have Docker compose V2 on your local machine.

Please note that docker Compose has been tested only under Linux but *in theory*,
it should work on MacOS and Windows too!

Last but not the least, there is a lot of shortcuts commands which live in the
**Makefile** of this project. You are strongly encourage to take a look if you
want to save some time (or if you don't know well Docker yet)!

### Deployment

To test various env build in another directory, you can use the
``deploy/deploy.sh`` script. More information are available in the
``README.md`` of that directory.

In any case, it is a good idea to take a look into it just to understand the
following steps below.

### Env files

Because secrets **must not** be available into containers (production only),
there is two env files, depending on your ENV:
* ``.env`` : This file is used by the Makefile and Docker compose build
* ``.env.dev | .env.prod``: This file is *mounted* into the container

You can safely copy this 3 files at the root of the project if you want to use
each env (local, dev, prod).

### Docker local

This setup is an hybrid: **only** services are docker containers (i.e: postgresql, redis)
and everything else live on your local machine.

You must first follow the "Local" section to meet all requirements needed:
virtualenv, poetry, npm, etc.
Then, you can setup the services with the following command:
````
cp env/.env.LOCAL .env # Edit it
cp folioblog/settings/local.py.dist folioblog/settings/local.py  # Edit if needed
make up
poetry install --without=prod
pre-commit install
npm install
npm run dist
python manage.py migrate
python manage.py createsuperuser
make initial_data  # OPTIONAL
python manage.py runserver
curl http://127.0.0.1:8000/admin
````

### Docker dev

This setup include docker containers for services but also for the Python app.
You still need git + pre-commit on your local machine, but that's it!

Then, you can setup the services with the following command :
````
cp env/.env.LOCAL .env # Edit it
cp env/.env.DEV .env.dev # Edit if needed
cp folioblog/settings/local.py.dist folioblog/settings/local.py  # Edit if needed
make up_wait
make initial_data_dev  # OPTIONAL
curl http://127.0.0.1:8000/admin  # Connect with admin/admin
````

All commands prefixed by "app" in the Makefile should interest you.

### Docker prod

This setup include Docker containers for services and the app, in a way more
close to a production environment.

The container's app is started by a WSGI server (gunicorn) behind a proxy
webserver (nginx) which will serve static files as well as HTTPS requests.

The connection is *secured* by a self-signed certificate (untrusted) that you
have to generate locally with OpenSSL. Your browser should complain about it
but you just have to accept it anyway.

This image is mainly intended to be built into CI pipelines but could also be
build locally for testing purpose.

You will have to:
````
cp env/.env.LOCAL .env # Edit it
cp env/.env.PROD .env.prod # Edit if needed
make certs
make up
make appmigrate
make appadmin
# make initial_data_prod  # OPTIONAL
curl https://folio.local/admin  # Connect with YOUR <FOLIOBLOG_ADMIN_USERNAME>/<FOLIOBLOG_ADMIN_PASSWD>
````

To play with multi-sites, the docker compose network add three aliases for the
proxy server and the SSL certificate *secure* them:
* folio.local
* demo.folio.local
* blog.folio.local

To use them, first update the wagtail sites hostnames in DB to match with.
To do so, go to: https://folio.local/admin/sites/

Then in order to use these domain names from your hosting machine, you must
edit your hosts file to add these entries to be forward to 127.0.0.1:
* on Linux, edit ``/etc/hosts``
* on Windows, edit ``c:\Windows\System32\Drivers\etc\hosts``

to add lines like:
````
127.0.0.1	folio.local
127.0.0.1	demo.folio.local
127.0.0.1	blog.folio.local
````

Finally, create a new site with hostname *demo.folio.local* and you should be
able to hit it: ``curl https://demo.folio.local``

### Local only

You have choose the hard and old school way... congratulations!

To locally get all the required tools, follow these next steps.

#### Backend

* Python 3.10 installed (virtualenv strongly recommanded)
* Install [poetry](https://python-poetry.org/docs/#installation).
* Run: `poetry install`

#### Frontend

* Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* `npm install`: install node packages
* `npm run dist`: copy node modules into django project

#### Databases

For now, only PostgreSQL is tested. In theory, other SGBD supported by Django
should work too.

*tips: for testing, don't forgot to set proper permissions for the connected
user (i.e: create and destroy DB testing).*

#### Redis

Redis could be used by [Django cache](https://docs.djangoproject.com/en/dev/topics/cache/).
This is not mandatory but strongly recommanded.

#### Pre-commit

Python binding package should be already installed by Poetry, so you just have
to do:
> pre-commit install

#### Selenium (end2end tests)

For end2end tests, download at least Chrome and its chromedriver (to put in PATH),
which is the only one browser supported for now.

For more details, see:
* [selenium doc](https://www.selenium.dev/documentation/)
* [selenium python doc](https://selenium-python.readthedocs.io/installation.html)

#### Local installation

Once requirements are set up, do the following steps:
````
cp folioblog/settings/local.py.dist folioblog/settings/local.py
vim folioblog/settings/local.py  # edit at least DATABASES and SECRET_KEY !
python manage.py migrate
python manage.py createsuperuser
./manage.py runserver 127.0.0.1:8000
google-chrome http://127.0.0.1:8000/admin &
````

## Performance

When you hit a new fresh page, it could be very slow due to the generation of
images renditions.

If you want to save some time, you could execute the following commands against
a running instance locally:
````
python manage.py runserver
python manage.py generaterenditions  # Generate rendtion for gallery full image
python manage.py loadcachepages  # Fetch all pages to generate renditions (and BTW, cache page if active)
````

And of course, against a docker container:
````
docker compose exec app python manage.py generaterenditions
docker compose exec app python manage.py loadcachepages
````

## Cron

There is some cron tasks you may need to set up.

Wagtail cron tasks:
````
docker compose exec app python manage.py fixtree --full
docker compose exec app python manage.py purge_revisions --days=30
docker compose exec app python manage.py publish_scheduled_pages
````

FolioBlog cron tasks:
````
# To generate gallery image thumbnails (before viewing them)
docker compose exec app python manage.py generaterenditions
# To fetch all pages in cache (if enabled)
docker compose exec app python manage.py loadcachepages
````
