#!/usr/bin/env bash

# Deploy a release of Monocle.
# The version number provided is expected to be without the leading v, e.g. 0.1.26

# check args count
if [ $# -ne 4 ]; then
  echo "Usage: $0 <environment - prod|dev> <version e.g. 0.1.1> <remote user> <deployment host address>"
  exit 1
fi

ENVIRONMENT=$1
VERSION=$2
REMOTE_USER=$3
REMOTE_HOST=$4

if [[ "$ENVIRONMENT" == "prod" ]]; then
  DOMAIN=monocle.pam.sanger.ac.uk
elif [[ "$ENVIRONMENT" == "dev" ]]; then
  DOMAIN=monocle.dev.pam.sanger.ac.uk
fi

# Pull the required tag
deploy_dir=$(mktemp -d -t monocle-XXXXXXXXXX)
git clone https://github.com/sanger-pathogens/monocle.git ${deploy_dir}
cd ${deploy_dir}
trap "{ if [[ -d ${deploy_dir} ]]; then rm -rf ${deploy_dir}; fi }" EXIT
git checkout tags/v${VERSION}

# Validate input args
source "${deploy_dir}/utils/common.sh"
validate_environment "${ENVIRONMENT}"
validate_version "${VERSION}"

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
# note: local variables are substituted as normal,
#       remote variables need escaping
#       (eg. VERSION vs API_SECRET_KEY)
ssh -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
    echo "Stopping existing containers..."
    docker-compose down
    echo "Setting configuration in docker-compose.yml..."
    sed -i -e "s/<VERSION>/${VERSION}/g" docker-compose.yml
    sed -i -e "s/<HOSTNAME>/${DOMAIN}/g" docker-compose.yml
    sed -i -e "s/<USER>/${REMOTE_USER}/g" docker-compose.yml
    sed -i -e "s/<SECRET_KEY>/\${API_SECRET_KEY}/g" docker-compose.yml
    echo "Setting configuration in UI's settings.js..."
    sed -i -e "s/<HOSTNAME>/${DOMAIN}/g" settings.js
    echo "Setting file permissions..."
    chmod 600 docker-compose.yml
    chmod 644 settings.js nginx.conf
    echo "Starting new containers..."
    docker-compose up -d
    echo "Done."
EOF

# close the connection
ssh -o ControlPath=%C -O exit $REMOTE_USER@$REMOTE_HOST
