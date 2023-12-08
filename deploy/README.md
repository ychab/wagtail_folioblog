This script help you to deploy **from scratch** the project on a Linux machine
through Docker compose for the following profile:

* **LOCAL** : python local with basic services compose.
* **DEV**: a full docker dev env.
* **PROD**: a *production's like* env.

# Requirements

You locally need to have installed at least:
* git
* docker compose V2

## Local

In addition, you need to have installed **globally**:
* Poetry
* NPM

## Dev

Nothing else required!

## Prod

In addition, you need to have installed on your system:
* OpenSSL to generate a self signed certificate.

* Also, don't forgot to locally add the following DNS aliases bind to 127.0.0.1:
  * folio.local
  * demo.folio.local
  * blog.folio.local

# Usage

To use this script, you must be in the following directory, and copy/edit config:
````
cd deploy
cp deploy.conf.sh.DIST deploy.conf.sh  # EDIT it
````

Finally, execute it from the current directory:
````
./deploy.sh local  # for local
./deploy.sh dev  # for dev
./deploy.sh prod  # for prod
````
