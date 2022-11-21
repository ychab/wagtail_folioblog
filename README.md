[![build](https://github.com/ychab/wagtail_folioblog/actions/workflows/build.yaml/badge.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/build.yaml)
[![lint](https://github.com/ychab/wagtail_folioblog/actions/workflows/lint.yaml/badge.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/lint.yaml)
[![precommit](https://github.com/ychab/wagtail_folioblog/actions/workflows/precommit.yaml/badge.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/precommit.yaml)
[![units](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/units.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/units.yaml)
[![NPM deps](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/npm-dependencies.svg)](https://github.com/ychab/wagtail_folioblog/actions/workflows/npm.yaml)
![licence](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/poetry-license.svg)
![folioblog version](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/poetry-version.svg)
![wagtail version](https://raw.githubusercontent.com/ychab/wagtail_folioblog/badges/.badges/main/poetry-wagtail-version.svg)

# FolioBlog, a Wagtail portfolio / blog demo

The FolioBlog project is the combination of a portfolio and a basic blog, build
with the powerful Wagtail CMS. It's main goal is to be a showcase for best
practices integrations with:

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

Integration / Automation:
* [Tox](https://tox.wiki/en/latest/)
* [Pre-commit](https://pre-commit.com/)
* [GitHub Action](https://github.com/features/actions)
* [Pylama](https://github.com/klen/pylama) and [isort](https://pycqa.github.io/isort/) for codingstyle

And yeah, that's my personal website! So please, don't hack me, I'm not famous!

## Requirements

### Backend

* For development:
  * you must first install [poetry](https://python-poetry.org/docs/#installation).
  * Once installed, just run: `poetry install`

* For testing (CI), no need to use poetry here, just do : `pip install -r requirements/dev.txt`

* For production, do instead : `pip install -r requirements/prod.txt`

*Note*: For now, only Python >= 3.10 is tested.

### Frontend

* first install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* `npm install`: install node packages
* `npm run dist`: copy node modules into django project

### Databases

Having access with proper permissions for one of the [supported SGDB by Django](https://docs.djangoproject.com/en/dev/ref/databases/).

#### PostgreSQL

For now, only this SGBD is tested. In theory, other supported SGBD should work.

*tips*: for local dev, don't forgot to set proper permissions for the connected
user (i.e: create and destroy DB testing).

#### Redis

Redis could be used by [Django cache](https://docs.djangoproject.com/en/dev/topics/cache/).
This is not mandatory but strongly recommanded.

### Pre-commit

Python binding package should be already installed by Poetry, so you just have
to do:
> pre-commit install

That's it!

**ugly tips**: If you want to skip check for a particular commit, do:
> git commit -m "blabla" --no-verify

but hope this is for good reasons huh!!

### Selenium (testing)

For end2end tests, download at least Chrome, its Chrome drivers and put it into
your PATH. For more details, [read the doc](https://selenium-python.readthedocs.io/installation.html#drivers).

## Get started

### Local installation

Once requirements are setup, do the following steps:
````
cp folioblog/settings/local.py.dist folioblog/settings/local.py
vim folioblog/settings/local.py  # edit at least DATABASES and SECRET_KEY !
python manage.py migrate
python manage.py createsuperuser
python manage.py fixtures load  # ONLY if you add fixtures yourself
./manage.py runserver 127.0.0.1:8000
google-chrome http://127.0.0.1:8000/admin &
````

*Tips*: take a look at the Makefile ;-)

### Page structures

By default, fixtures have been removed and thus, the database is empty.

Here is the pages tree:
* Root page
  * PortFolio page
    * Home index
    * Blog index
      * Blog pages
    * Gallery
    * Video index
      * Video pages
    * Search index
    * some basic pages (cookies policy, disclaimer, presentation)
