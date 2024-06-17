#!/bin/bash

init() {
  # Load config if any
  if [ -f deploy.conf.sh ]; then
      echo "-> Load deploy conf"
      source deploy.conf.sh
  else
      echo "-> No deploy.conf.sh founded... exit!"
      exit 1
  fi

  # Build PATH var is required
  if [ -z "${BUILD_PATH}" ]; then
      echo "-> No BUILD_PATH env var founded... exit!"
      exit 1
  fi

  # Set default values
  if [ -z "$FOLIOBLOG_VERSION" ]; then
      echo "-> Set default value for FOLIOBLOG_VERSION to 'main'"
      FOLIOBLOG_VERSION=main
  fi

  if [ -z "${PYTHON_EXECUTABLE}" ]; then
      if [ -n "${PYENV_ROOT}" ]; then
          PYTHON_EXECUTABLE=$(pyenv which python)
      else
          PYTHON_EXECUTABLE=$(which python)
      fi
      echo "-> Set default value for PYTHON_EXECUTABLE to $PYTHON_EXECUTABLE"
  fi

  # Detect if restore is enabled
  HAS_RESTORE=1
  for ENV_VAR in FOLIOBLOG_BACKUP_HOST FOLIOBLOG_BACKUP_PATH_SQL FOLIOBLOG_BACKUP_PATH_MEDIA; do
      if [ -z "${!ENV_VAR}" ]; then
          HAS_RESTORE=0
          break
      fi
  done
}

git_clone() {
    echo -e "\n-> Cloning repo and switching branch\n"
    rm -Rf $PROJECT_PATH
    git clone --branch $FOLIOBLOG_VERSION https://github.com/ychab/wagtail_folioblog.git $PROJECT_PATH
}

deploy_local() {
    PROJECT_PATH="$BUILD_PATH/local"

    # Source code
    git_clone
    cd $PROJECT_PATH || exit

    # Settings
    echo -e "\n-> Preparing settings\n"
    cp env/.env.LOCAL .env
    cp folioblog/settings/local.py.dist folioblog/settings/local.py

    # Virtualenv
    echo -e "\n-> Preparing virtualenv\n"
    $PYTHON_EXECUTABLE -m venv .venv
    source .venv/bin/activate

    # Poetry
    poetry install --no-interaction --without=prod
    poetry run pre-commit install

    # Node
    echo -e "\n-> Run NPM"
    npm install
    npm run dist

    # Cleanup containers
    echo -e "\n-> Cleanup containers\n"
    make down_clean

    # Restore containers OR up
    if [ $HAS_RESTORE = 1 ]; then
        sed -i 's,^# FOLIOBLOG_BACKUP_HOST=.*,FOLIOBLOG_BACKUP_HOST='"$FOLIOBLOG_BACKUP_HOST"',g' .env
        sed -i 's,^# FOLIOBLOG_BACKUP_PATH_SQL=.*,FOLIOBLOG_BACKUP_PATH_SQL='"$FOLIOBLOG_BACKUP_PATH_SQL"',g' .env
        sed -i 's,^# FOLIOBLOG_BACKUP_PATH_MEDIA=.*,FOLIOBLOG_BACKUP_PATH_MEDIA='"$FOLIOBLOG_BACKUP_PATH_MEDIA"',g' .env

        echo -e "\n-> Restore DB and media\n"
        poetry run make restore_local
        poetry run python manage.py migrate --noinput
    else
        echo -e "\n-> Up containers and restore initial data\n"
        make up_wait
        poetry run python manage.py migrate --noinput
        poetry run python manage.py createadmin --username=admin --password=admin
        poetry run make initial_data
    fi

    echo -e "\nBUILD finished!\n"
    echo "To run the project, execute:"
    echo "> cd $BUILD_PATH/local"
    echo "> poetry run python manage.py runserver"
}

deploy_dev() {
    PROJECT_PATH="$BUILD_PATH/dev"

    # Source code
    git_clone
    cd $PROJECT_PATH || exit

    # Settings
    echo -e "\n-> Preparing settings\n"
    cp env/.env.LOCAL .env
    cp env/.env.DEV .env.dev
    cp folioblog/settings/local.py.dist folioblog/settings/local.py
    sed -i 's,# COMPOSE_FILE=docker-compose.yaml:docker-compose.dev.yaml,COMPOSE_FILE=docker-compose.yaml:docker-compose.dev.yaml,g' .env
    sed -i 's,^# FOLIOBLOG_UID=.*,FOLIOBLOG_UID='"${FOLIOBLOG_UID:-1000}"',g' .env
    sed -i 's,^# FOLIOBLOG_GID=.*,FOLIOBLOG_GID='"${FOLIOBLOG_GID:-1000}"',g' .env
    sed -i 's,^# FOLIOBLOG_REDIS_LOCATION=.*,FOLIOBLOG_REDIS_LOCATION='"${FOLIOBLOG_REDIS_LOCATION:-}"',g' .env.dev

    # Cleanup containers
    echo -e "\n-> Cleanup containers\n"
    make down_clean

    # Rebuild image just in case
    echo -e "\n-> Rebuild DEV image\n"
    make rebuild

    # Create container and init it for the first time (NPM build)
    echo -e "\n-> Up containers\n"
    make up_wait

    # Restore containers
    if [ $HAS_RESTORE = 1 ]; then
        sed -i 's,^# FOLIOBLOG_BACKUP_HOST=.*,FOLIOBLOG_BACKUP_HOST='"$FOLIOBLOG_BACKUP_HOST"',g' .env
        sed -i 's,^# FOLIOBLOG_BACKUP_PATH_SQL=.*,FOLIOBLOG_BACKUP_PATH_SQL='"$FOLIOBLOG_BACKUP_PATH_SQL"',g' .env
        sed -i 's,^# FOLIOBLOG_BACKUP_PATH_MEDIA=.*,FOLIOBLOG_BACKUP_PATH_MEDIA='"$FOLIOBLOG_BACKUP_PATH_MEDIA"',g' .env

        echo -e "\n-> Restore DB and media\n"
        make restore_dev
        make appmigrate
    else
        echo -e "\n-> Restore initial data\n"
        make initial_data_dev
    fi

    echo -e "\nBUILD finished!\n"
    echo "You can check http://127.0.0.1:8000/admin"
}

deploy_prod() {
    PROJECT_PATH="$BUILD_PATH/prod"

    # Source code
    git_clone
    cd $PROJECT_PATH || exit

    # Settings
    echo -e "\n-> Preparing settings\n"
    cp env/.env.LOCAL .env
    cp env/.env.PROD .env.prod
    sed -i 's,# COMPOSE_FILE=docker-compose.yaml:docker-compose.prod.yaml,COMPOSE_FILE=docker-compose.yaml:docker-compose.prod.yaml,g' .env
    sed -i 's,^# FOLIOBLOG_ADMIN_USERNAME=.*,FOLIOBLOG_ADMIN_USERNAME='"${FOLIOBLOG_ADMIN_USERNAME:-admin}"',g' .env
    sed -i 's,^# FOLIOBLOG_ADMIN_PASSWD=.*,FOLIOBLOG_ADMIN_PASSWD='"${FOLIOBLOG_ADMIN_PASSWD:-admin}"',g' .env
    sed -i 's,^# FOLIOBLOG_NGINX_PORT=.*,FOLIOBLOG_NGINX_PORT=80,g' .env
    sed -i 's,^# FOLIOBLOG_NGINX_PORT_SSL=.*,FOLIOBLOG_NGINX_PORT_SSL=443,g' .env
    sed -i 's,^# FOLIOBLOG_SECRET_KEY=.*,FOLIOBLOG_SECRET_KEY='"${FOLIOBLOG_SECRET_KEY:-bla-bla-bla}"',g' .env
    sed -i 's,^# FOLIOBLOG_EMAIL_HOST_PASSWORD=.*,FOLIOBLOG_EMAIL_HOST_PASSWORD='"${FOLIOBLOG_EMAIL_HOST_PASSWORD:-}"',g' .env
    sed -i 's,^# FOLIOBLOG_NGINX_HOST=.*,FOLIOBLOG_NGINX_HOST=folio.local blog.folio.local demo.folio.local,g' .env
    sed -i 's,^# FOLIOBLOG_NGINX_SSL_CERT=.*,FOLIOBLOG_NGINX_SSL_CERT=folio-selfsigned.crt,g' .env
    sed -i 's,^# FOLIOBLOG_NGINX_SSL_KEY=.*,FOLIOBLOG_NGINX_SSL_KEY=folio-selfsigned.key,g' .env

    # Generate certs
    make certs

   # Cleanup containers
    echo -e "\n-> Cleanup containers\n"
    make down_clean

    # Rebuild image just in case
    echo -e "\n-> Rebuild PROD image\n"
    make rebuild

    # Create container and init it (superuser & co).
    echo -e "\n-> Up containers\n"
    make up

    # Restore containers OR up
    if [ $HAS_RESTORE = 1 ]; then
        sed -i 's,^# FOLIOBLOG_BACKUP_HOST=.*,FOLIOBLOG_BACKUP_HOST='"$FOLIOBLOG_BACKUP_HOST"',g' .env
        sed -i 's,^# FOLIOBLOG_BACKUP_PATH_SQL=.*,FOLIOBLOG_BACKUP_PATH_SQL='"$FOLIOBLOG_BACKUP_PATH_SQL"',g' .env
        sed -i 's,^# FOLIOBLOG_BACKUP_PATH_MEDIA=.*,FOLIOBLOG_BACKUP_PATH_MEDIA='"$FOLIOBLOG_BACKUP_PATH_MEDIA"',g' .env

        echo -e "\n-> Restore DB and media\n"
        make restore_prod
        make appmigrate
    else
        echo -e "\n-> Restore initial data\n"
        make appmigrate
        make appadmin
        make initial_data_prod
    fi

    echo -e "\nBUILD finished!\n"
    echo "You can check https://folio.local/admin"
}

# Main
if [ -z "$1" ]; then
    echo -e "MISSING first argument, possible values: local | dev | prod"
else
  init
  if [ $1 = 'local' ]; then
      echo -e "\n-> Executing LOCAL env"
      deploy_local
  elif [ $1 = 'dev' ]; then
      echo -e "\n-> Executing DEV env"
      deploy_dev
  elif [ $1 = 'prod' ]; then
      echo -e "\n-> Executing PROD env"
      deploy_prod
  fi
fi
