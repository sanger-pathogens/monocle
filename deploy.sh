#!/usr/bin/env bash

# Deploy a release of Monocle.

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/utils/common.sh"

# check args count
if [ $# -ne 2 ]; then
  echo "Usage: $0 <version> <prod|dev>"
  exit 1
fi

VERSION=$1
validate_version "${VERSION}"

ENVIRONMENT=$2
validate_environment "${ENVIRONMENT}"

REMOTE_USER=pathpipe
if [[ "$ENVIRONMENT" == "prod" ]]; then
  REMOTE_HOST=monocle.pam.sanger.ac.uk
elif [[ "$ENVIRONMENT" == "dev" ]]; then
  REMOTE_HOST=monocle.dev.pam.sanger.ac.uk
fi

# copy production compose file (template)
# keep connection to avoid multiple password entries
scp -o ControlMaster=yes \
    -o ControlPersist=yes \
    -o ControlPath=%C \
    docker-compose.prod.yml $REMOTE_USER@$REMOTE_HOST:~/docker-compose.yml

# copy production settings file, nginx config
# (may want to remove from git long term)
scp -o ControlPath=%C ui/settings.prod.js $REMOTE_USER@$REMOTE_HOST:~/settings.js
scp -o ControlPath=%C ui/nginx.prod.conf $REMOTE_USER@$REMOTE_HOST:~/nginx.conf

# replace the running version
# using existing connection
ssh -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
    echo "Stopping existing containers..."
    docker-compose down

    # load secrets from host
    source ~/.monocle-secrets

    echo "Setting configuration in docker-compose.yml..."
    sed -i -e "s/<VERSION>/${VERSION}/g" docker-compose.yml
    sed -i -e "s/<HOSTNAME>/${REMOTE_HOST}/g" docker-compose.yml
    sed -i -e "s/<SECRET_KEY>/${API_SECRET_KEY}/g" docker-compose.yml
    
    echo "Setting configuration in UI's settings.js..."
    sed -i -e "s/<HOSTNAME>/${REMOTE_HOST}/g" settings.js

    echo "Starting new containers..."
    docker-compose up -d

    echo "Done."
EOF

# close the connection
ssh -o ControlPath=%C -O exit $REMOTE_USER@$REMOTE_HOST
