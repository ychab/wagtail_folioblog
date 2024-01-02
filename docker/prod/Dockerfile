#################
# Pre build stage
#################

FROM python:3.10-slim-buster AS build_app
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    NODE_VERSION=v20.10.0 \
    DJANGO_SETTINGS_MODULE="folioblog.settings.prod"
ENV PATH=/venv/bin:/opt/node-${NODE_VERSION}-linux-x64/bin:$PATH

WORKDIR /app

# Copy required source only
COPY ./requirements/prod.txt /app/requirements.txt
COPY ./manage.py ./package* ./docker/prod/gunicorn.py /app/
COPY ./dist /app/dist
COPY ./folioblog /app/folioblog
COPY ./docker/prod/local.py /app/folioblog/settings/local.py

RUN apt update --yes --quiet && apt install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    tar \
    xz-utils

# Install node (with npm) needed by Django Compressor (uglifyJS).
RUN wget -O /opt/node.tar.xz https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.xz && \
    tar xfJ /opt/node.tar.xz -C /opt/ --no-same-owner && \
    npm install -g npm@latest

# Build frontend sources
RUN npm install --omit=dev && \
    npm run dist

# Create virtualenv and install backend dependencies.
RUN python -m venv /venv && \
    pip install --upgrade pip setuptools && \
    pip install -r /app/requirements.txt

# Prepare static dirs, collect, compress and cleanup
RUN mkdir /app/media /app/static && \
    # Collect static files.
    FOLIOBLOG_LANGUAGE_CODE=en \
    FOLIOBLOG_SECRET_KEY_DUMMY=dummy-key \
    python manage.py collectstatic --noinput --clear && \
    # Compress static files.
    FOLIOBLOG_LANGUAGE_CODE=en \
    FOLIOBLOG_SECRET_KEY_DUMMY=dummy-key \
    python manage.py compress && \
    # Cleanup sources for next copies.
    rm -Rf ./node_modules ./dist ./package*

##########################
# Final build stage ALPINE
##########################

FROM python:3.10-alpine3.19
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH=/venv/bin:$PATH \
    DJANGO_SETTINGS_MODULE="folioblog.settings.prod"

WORKDIR /app

# Create an app user.
RUN adduser --disabled-password --no-create-home --shell /bin/bash appuser

# Only copy pre-build app from next steps.
COPY --chown=appuser:appuser --from=build_app /app /app

RUN apk update && \
    # Install build dependencies temporary
    apk add --no-cache --virtual build_deps \
        build-base \
        postgresql-dev && \
    # Install required system dependencies
    apk add --no-cache \
        bash \
        libpq-dev \
        libjpeg-turbo-dev \
        libpng-dev \
        libwebp-dev \
        zlib-dev && \
    # Create virtualenv and install backend dependencies with gunicorn.
    python -m venv /venv && \
    pip install --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    # Remove build deps
    apk del build_deps

USER appuser
EXPOSE 8000
VOLUME ["/app/media", "/app/static"]
CMD ["gunicorn", "folioblog.wsgi", "-c", "gunicorn.py"]
