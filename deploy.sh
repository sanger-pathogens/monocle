#!/usr/bin/env bash

# Deploy a release of Monocle.
# The version number provided is expected to be without the leading v, e.g. 0.1.26
# Running with '-m yes' will run the release django database migrations.

usage() {
  echo "Usage: $0 -e|--env <environment - prod|dev> -v|--version <version e.g. 0.1.1>" \
    "-m|--migrate-db <yes|no> -u|--user <remote user id> -h|--host <deployment host address>"
  exit 1
}

ENVIRONMENT=
VERSION=
REMOTE_USER=
REMOTE_HOST=
APPLY_MIGRATIONS=

# read command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case "$key" in
      -e|--env)
      shift
      ENVIRONMENT="$1"
      ;;
      -e=*|--env=*)
      ENVIRONMENT="${key#*=}"
      ;;

      -v|--version)
      shift
      VERSION="$1"
      ;;
      -v=*|--version=*)
      VERSION="${key#*=}"
      ;;

      -u|--user)
      shift
      REMOTE_USER="$1"
      ;;
      -u=*|--user=*)
      REMOTE_USER="${key#*=}"
      ;;

      -h|--host)
      shift
      REMOTE_HOST="$1"
      ;;
      -h=*|--host=*)
      REMOTE_HOST="${key#*=}"
      ;;

      -m|--migrate-db)
      shift
      APPLY_MIGRATIONS="$1"
      ;;
      -m=*|--migrate-db=*)
      APPLY_MIGRATIONS="${key#*=}"
      ;;

      *)
      echo "Unknown option '$key'"
      usage
      ;;
    esac
    # shift after checking all the cases to get the next option
    shift
done

# basic arg validation
if  [[ -z "${ENVIRONMENT}" ]] || [[ -z "${VERSION}" ]] ||
    [[ -z "${REMOTE_USER}" ]] || [[ -z "${REMOTE_HOST}" ]] ||
    [[ -z "${APPLY_MIGRATIONS}" ]] || [[ "${APPLY_MIGRATIONS}" != "yes" && "${APPLY_MIGRATIONS}" != "no" ]]
then
    usage
fi

if [[ "$ENVIRONMENT" == "prod" ]]; then
    DOMAIN=monocle.pam.sanger.ac.uk
    PUBLIC_DOMAIN=monocle.sanger.ac.uk
elif [[ "$ENVIRONMENT" == "dev" ]]; then
    DOMAIN=monocle.dev.pam.sanger.ac.uk
    PUBLIC_DOMAIN=
else
    usage
fi

# pull the required tag
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

# copy production settings file, nginx config, metadata api config
# (may want to remove from git long term)
scp -o ControlPath=%C ui/settings.prod.js $REMOTE_USER@$REMOTE_HOST:~/settings.js
scp -o ControlPath=%C ui/nginx.prod.conf $REMOTE_USER@$REMOTE_HOST:~/nginx.conf
scp -o ControlPath=%C metadata/juno/config.json $REMOTE_USER@$REMOTE_HOST:~/metadata-api.json

# replace the running version
# using existing connection
# note: local variables are substituted as normal,
#       remote variables need escaping
#       (eg. VERSION vs API_SECRET_KEY)
ssh -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
    set -e
    echo "Stopping existing containers..."
    docker-compose down
    echo "Setting configuration in docker-compose.yml..."
    sed -i -e "s/<VERSION>/v${VERSION}/g" docker-compose.yml
    sed -i -e "s/<HOSTNAME>/${DOMAIN}/g" docker-compose.yml
    sed -i -e "s/<HOSTNAME_PUBLIC>/${PUBLIC_DOMAIN}/g" docker-compose.yml
    sed -i -e "s/<USER>/${REMOTE_USER}/g" docker-compose.yml
    sed -i -e "s/<SECRET_KEY>/\${API_SECRET_KEY}/g" docker-compose.yml
    echo "Setting configuration in UI's settings.js..."
    sed -i -e "s/<HOSTNAME>/${DOMAIN}/g" settings.js
    echo "Setting file permissions..."
    chmod 600 docker-compose.yml metadata-api.json
    chmod 644 settings.js nginx.conf
    echo "Pulling version v${VERSION} images..."
    docker-compose pull
    status=0
    if [[ "${APPLY_MIGRATIONS}" == "yes" ]]
    then
        echo "Applying database migrations..."
        docker-compose run --no-deps --rm api python manage.py migrate
        status=\$?
        if [[ \${status} -ne 0 ]]
        then
            echo "FATAL ERROR: Database migration returned non-zero status: \${status}"
        fi
    fi
    if [[ \${status} -eq 0 ]]
    then
        echo "Starting containers..."
        docker-compose up -d
        echo "Done."
    fi
EOF

# close the connection
ssh -o ControlPath=%C -O exit $REMOTE_USER@$REMOTE_HOST
