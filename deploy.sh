#!/usr/bin/env bash

# Deploy a release of Monocle.

VERSION=$1
REMOTE_USER=pathpipe
REMOTE_HOST=172.27.82.31

# copy production compose file (template)
# keep connection to avoid multiple password entries
scp -o ControlMaster=yes \
    -o ControlPersist=yes \
    -o ControlPath=%C \
    docker-compose.prod.yml $REMOTE_USER@$REMOTE_HOST:~/docker-compose.yml

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
