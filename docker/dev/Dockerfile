FROM python:3.10-slim-buster

ARG UID
ARG GID
ARG NODE_VERSION
ARG POETRY_VERSION

# Force Python stdout and stderr streams to be unbuffered.
# BTW, don't collect pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # Poetry
    POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    \
    VIRTUAL_ENV=/venv \
    PATH=/venv/bin:/opt/poetry/bin:/opt/node-${NODE_VERSION}-linux-x64/bin:$PATH \
    DJANGO_SETTINGS_MODULE="folioblog.settings.dev"

# Install missing system dependencies first.
RUN apt update --yes --quiet && apt install --yes --quiet --no-install-recommends \
    libjpeg62-turbo-dev \
    libpq-dev \
    libwebp-dev \
    zlib1g-dev \
    gettext \
    wget \
    curl \
    unzip \
    tar \
    xz-utils

# Install all packages for chromedriver.
RUN apt install --yes --no-install-recommends xvfb gnupg && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt update --yes && \
    apt install --yes google-chrome-stable && \
    CHROME_VERSION=$(google-chrome --version | cut -f 3 -d ' ' | cut -d '.' -f 1) && \
    CHROMEDRIVER_RELEASE=$(curl --location --fail --retry 3 https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}) && \
    curl --silent --show-error --location --fail --retry 3 --output /tmp/chromedriver_linux64.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_RELEASE/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver_linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# Create an app user instead of playing with Docker compose "user" service attribute.
# Indead, having a user on the fly without home is not enough for Poetry, NPM, chromedriver.
RUN groupadd --gid=${GID} appuser && \
    useradd --uid=${UID} --gid=${GID} --create-home --shell /bin/bash appuser

# Then install Poetry.
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry self update --no-interaction && \
    $POETRY_HOME/venv/bin/pip install poetry-plugin-export

# Then install nodeJS with NPM.
RUN wget -O /opt/node.tar.xz https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.xz && \
    tar xfJ /opt/node.tar.xz -C /opt/ --no-same-owner && \
    npm install -g npm@latest && \
    rm /opt/node.tar.xz

# Just copy necessary files, local files would be mounted into container.
COPY --chown=appuser:appuser pyproject.toml poetry.lock /app/

# Prepare build directories for appuser.
RUN mkdir ${VIRTUAL_ENV} && \
    chown appuser:appuser ${VIRTUAL_ENV}

# Move to app dir and switch to user appuser.
WORKDIR /app
USER appuser

# Create virtualenv and install into deps with Poetry as appuser.
RUN python -m venv ${VIRTUAL_ENV} && \
    pip install --upgrade pip setuptools && \
    poetry install --no-interaction --no-cache

EXPOSE 8000
ENTRYPOINT ["docker/dev/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
