# Use the default Python image to have more reposities availables.
FROM python:3.10-slim

ARG FOLIOBLOG_RELEASE
ARG NODE_VERSION
ARG MEDIA_ROOT
ARG STATIC_ROOT

# Force Python stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    VIRTUAL_ENV=/venv \
    PATH=/venv/bin:/opt/node-${NODE_VERSION}-linux-x64/bin:$PATH \
    DJANGO_SETTINGS_MODULE="folioblog.settings.prod"

# Install missing system dependencies first.
RUN apt update --yes --quiet && apt install --yes --quiet --no-install-recommends \
    libjpeg62-turbo-dev \
    libpq-dev \
    libwebp-dev \
    zlib1g-dev \
    wget \
    curl \
    tar \
    git \
    xz-utils

# Then install nodeJS with NPM.
RUN wget -O /opt/node.tar.xz https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.xz
RUN tar xfJ /opt/node.tar.xz -C /opt/ --no-same-owner
RUN npm install -g npm@latest
RUN rm /opt/node.tar.xz

# Create an app user.
RUN useradd --create-home --shell /bin/bash appuser

# Fetch source with git for simplicity
RUN git clone --depth=1 --branch=${FOLIOBLOG_RELEASE} https://github.com/ychab/wagtail_folioblog.git /app
RUN chown -R appuser:appuser /app

# Create virtualenv and install backend dependencies with gunicorn.
RUN python -m venv ${VIRTUAL_ENV}
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r /app/requirements/prod.txt
RUN pip install --no-cache-dir gunicorn

USER appuser

WORKDIR /app

# Install frontend dependencies and build final files.
RUN npm install --omit=dev
RUN npm run dist

# Prepare local settings from .env files
RUN cp /app/docker/prod/local.py /app/folioblog/settings/local.py

# Create files directories if not already exists.
RUN mkdir -p $STATIC_ROOT
RUN mkdir -p $MEDIA_ROOT

# Collect static files.
RUN FOLIOBLOG_LANGUAGE_CODE=en \
    FOLIOBLOG_SECRET_KEY_DUMMY=dummy-key \
    FOLIOBLOG_STATIC_ROOT=$STATIC_ROOT \
    python manage.py collectstatic --noinput --clear

# Then compress static files.
RUN FOLIOBLOG_LANGUAGE_CODE=en \
    FOLIOBLOG_SECRET_KEY_DUMMY=dummy-key \
    FOLIOBLOG_STATIC_ROOT=$STATIC_ROOT \
    python manage.py compress

EXPOSE 8000

# FOR PURPOSE ONLY, add a script to execute commands at container startup.
# In theory, these commands must be executed elsewhere, depending on your infra.
ENTRYPOINT ["docker/prod/entrypoint.sh"]

CMD ["gunicorn", "folioblog.wsgi", "-c", "docker/prod/gunicorn.py"]
