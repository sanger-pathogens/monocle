#!/usr/bin/env bash

set -x
set -e

VERSION=$1

# copy production compose file (template)
# keep connection to avoid multiple password entries
scp -o ControlMaster=yes \
    -o ControlPersist=yes \
    -o ControlPath=%C \
    docker-compose.prod.yml pathpipe@172.27.82.31:~/docker-compose.yml

# replace the running version
# using existing connection
ssh -o ControlPath=%C pathpipe@172.27.82.31 << EOF
    echo "Stopping existing containers..."
    docker-compose down

    echo "Setting version in docker-compose.yml..."
    sed -i -e "s/VERSION/${VERSION}/g" docker-compose.yml
    
    echo "Starting new containers..."
    docker-compose up -d

    echo "Done."
EOF

# close the connection
ssh -o ControlPath=%C -O exit pathpipe@172.27.82.31
