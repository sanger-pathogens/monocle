#!/usr/bin/env bash

# Deploy a release of Monocle.

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/utils/common.sh"

# check args count
if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION=$1
validate_version "${VERSION}"

REMOTE_USER=pathpipe
REMOTE_HOST=monocle.dev.pam.sanger.ac.uk

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

    echo "Setting version in docker-compose.yml..."
    sed -i -e "s/VERSION/${VERSION}/g" docker-compose.yml
    
    echo "Starting new containers..."
    docker-compose up -d

    echo "Done."
EOF

# close the connection
ssh -o ControlPath=%C -O exit $REMOTE_USER@$REMOTE_HOST
