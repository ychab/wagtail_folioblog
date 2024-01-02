######################
# Frontend build stage
######################

FROM node:20.10.0 AS build_front
WORKDIR /app
COPY ./package* .
COPY ./dist dist
RUN mkdir -p folioblog/static && \
    npm install --omit=dev && \
    npm run dist

#####################
# Backend build stage
#####################

FROM python:3.10-slim-buster AS build_back
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    NODE_VERSION=v20.10.0 \
    DJANGO_SETTINGS_MODULE="folioblog.settings.prod"
ENV PATH=/venv/bin:/opt/node-${NODE_VERSION}-linux-x64/bin:$PATH

WORKDIR /app

# Copy required source only
COPY ./folioblog /app/folioblog
COPY --from=build_front /app/node_modules /app/node_modules
COPY --from=build_front /app/folioblog/static /app/folioblog/static
COPY ./manage.py /app/
COPY ./requirements/prod.txt /app/requirements.txt
COPY ./docker/prod/local.py /app/folioblog/settings/local.py
COPY ./docker/prod/gunicorn.py /app/

RUN apt update --yes --quiet && apt install --yes --quiet --no-install-recommends \
    libpq-dev \
    wget \
    tar \
    xz-utils && \
    # Install node (with npm) needed by Django Compressor (uglifyJS).
    wget -O /opt/node.tar.xz https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.xz && \
    tar xfJ /opt/node.tar.xz -C /opt/ --no-same-owner && \
    npm install -g npm@latest && \
    # Create virtualenv and install backend dependencies.
    python -m venv /venv && \
    pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    # Prepare directories \
    mkdir /app/media /app/static && \
    # Collect static files.
    FOLIOBLOG_LANGUAGE_CODE=en \
    FOLIOBLOG_SECRET_KEY_DUMMY=dummy-key \
    python manage.py collectstatic --noinput --clear && \
    # Compress static files.
    FOLIOBLOG_LANGUAGE_CODE=en \
    FOLIOBLOG_SECRET_KEY_DUMMY=dummy-key \
    python manage.py compress && \
    # Cleanup sources for next copies.
    rm -Rf node_modules

###################
# Final build stage
###################

FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED=1 \
    PATH=/venv/bin:$PATH \
    DJANGO_SETTINGS_MODULE="folioblog.settings.prod"

WORKDIR /app

RUN apt update --yes --quiet && apt install --yes --quiet --no-install-recommends  \
    libjpeg62-turbo-dev \
    libpq-dev \
    libwebp-dev \
    zlib1g-dev && \
    # Create an app user.
    useradd --no-create-home --shell /bin/bash appuser

# Only copy pre-build app and venv by next steps.
COPY --chown=appuser:appuser --from=build_back /app /app
COPY --chown=appuser:appuser --from=build_back /venv /venv

USER appuser
EXPOSE 8000
VOLUME ["/app/media", "/app/static"]
CMD ["gunicorn", "folioblog.wsgi", "-c", "gunicorn.py"]
