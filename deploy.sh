#!/usr/bin/env bash

# Deploy a release of Monocle.
# The version number provided is expected to be without the leading v, e.g. 0.1.26
# Running with '-m yes' will run the release django database migrations.

usage() {
  echo "Usage: $0 arguments [options]
       
       Mandatory arguments:
       -e --env         deployed environment: \`prod\` or \`dev\` 
       -m --migrate_db  run an associated database release: \`yes\` or \`no\`
       -u --user        user id on deployment host
       -h --host        deployment host name or IP address
       
       Options:
       -v --version     version number without \`v\` prefix
                        IMPORTANT: if this is not provided, then both
                        \`--branch\` and \`--tag\` must be specified
       -d --domain      service domain name; overrides the default based on
                        the deployed environment (set by \`--env\`)
       -b --branch      deploy from this branch instead of git tag derived
                        from version number (set by \`--version\`)
       -t --tag         docker images tag; overrides tag derived from version
                        number (set by \`--version\`)
       (There is no option to set the public domain for the service, as
       that feature is reserved for the production environment.)
  
       Example 1: deploy to pathogens_dev instance:
       $0 -e dev -v 0.1.45 -m no -u ubuntu -h monocle_vm.dev.pam.sanger.ac.uk
          
       Example 2: deploy unstable (pre-release) version as \`dev_user@localhost\`
       $0 -e dev -m no -u dev_user -h localhost --domain localhost --branch master --tag unstable
          
       Example 3: deploy as \`dev_user@localhost\`, from feature branch
                  \`some_feature_branch\`, using docker images built from
                  commit \`ae48f554\`:
       $0 -e dev -m no -u dev_user -h localhost --domain localhost --branch some_feature_branch --tag commit-ae48f554
"
  exit 1
}

ENVIRONMENT=
VERSION=
REMOTE_USER=
REMOTE_HOST=
APPLY_MIGRATIONS=

ECHO_EM=$(tput bold)
ECHO_RESET=$(tput sgr0)

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

      -d|--domain)
      shift
      OPT_DOMAIN="$1"
      ;;
      -d=*|--domain=*)
      OPT_DOMAIN="${key#*=}"
      ;;

      -b|--branch)
      shift
      OPT_BRANCH="$1"
      ;;
      -b=*|--branch=*)
      OPT_BRANCH="${key#*=}"
      ;;

      -t|--tag)
      shift
      OPT_TAG="$1"
      ;;
      -t=*|--tag=*)
      OPT_TAG="${key#*=}"
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
if  [[ -z "${ENVIRONMENT}" ]] ||
    [[ -z "${REMOTE_USER}" ]] || [[ -z "${REMOTE_HOST}" ]] ||
    [[ -z "${APPLY_MIGRATIONS}" ]] || [[ "${APPLY_MIGRATIONS}" != "yes" && "${APPLY_MIGRATIONS}" != "no" ]]
then
    usage
fi

# if no version, then branch and tag must be specified
if [[ -z "${VERSION}" ]] && [[ -z "${OPT_BRANCH}" || -z "${OPT_TAG}" ]]
then
   echo "${ECHO_EM}When not using --version is given, --branch and --tag must both be provided${ECHO_RESET}"
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

if [[ ! -z "$OPT_DOMAIN" ]]; then
   echo "${ECHO_EM}Service will use domain ${OPT_DOMAIN} in place of ${DOMAIN}${ECHO_RESET}"
   DOMAIN="$OPT_DOMAIN"
fi

# pull the required git tag, or branch
deploy_dir=$(mktemp -d -t monocle-XXXXXXXXXX)
git clone git@gitlab.internal.sanger.ac.uk:sanger-pathogens/monocle.git ${deploy_dir}
cd ${deploy_dir}
trap "{ if [[ -d ${deploy_dir} ]]; then rm -rf ${deploy_dir}; fi }" EXIT
if [[ ! -z "$OPT_BRANCH" ]]; then
   echo "${ECHO_EM}Checking out ${OPT_BRANCH} in place of version number tag${ECHO_RESET}"
   git switch "$OPT_BRANCH"
else
   git checkout "tags/v${VERSION}"
fi

docker_tag="v${VERSION}"
if [[ ! -z "$OPT_TAG" ]]; then
   echo "${ECHO_EM}Using docker images with tag ${OPT_TAG} in place of version number tag${ECHO_RESET}"
   docker_tag="$OPT_TAG"
fi

# Validate input args
source "${deploy_dir}/utils/common.sh"
validate_environment "${ENVIRONMENT}"
if [[ ! -z "${VERSION}" ]]; then
   validate_version "${VERSION}"
fi

# Check the database release file exists
DB_MIGRATION_SQL_FILE="./database/releases/${VERSION}/release.sql"
if [[ "${APPLY_MIGRATIONS}" == "yes" ]] && [[ ! -f "${DB_MIGRATION_SQL_FILE}" ]]
then
    echo "FATAL ERROR: Unable to find the database release file: ${DB_MIGRATION_SQL_FILE}"
    echo "Release aborted - no changes have been applied"
    echo "If you do not need a database release, then specify the '-m no' flag"
    exit 2
fi

# shut down applications first
# keep connection to avoid multiple password entries
ssh -o ControlMaster=yes -o ControlPersist=yes -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
    set -e
    echo "Stopping existing containers..."
    docker-compose down
EOF

# copy production compose file (template)
scp -o ControlPath=%C docker-compose.prod.yml $REMOTE_USER@$REMOTE_HOST:~/docker-compose.yml

# copy production nginx config (for proxy and ui), metadata api config
# (may want to remove from git long term)
scp -o ControlPath=%C proxy/nginx.prod.proxy.conf  $REMOTE_USER@$REMOTE_HOST:~/nginx.proxy.conf
scp -o ControlPath=%C ui/nginx.prod.ui.conf        $REMOTE_USER@$REMOTE_HOST:~/nginx.ui.conf
scp -o ControlPath=%C metadata/juno/config.json    $REMOTE_USER@$REMOTE_HOST:~/metadata-api.json

# replace the running version
# using existing connection
# note: local variables are substituted as normal,
#       remote variables need escaping
#       (eg. VERSION vs API_SECRET_KEY)
ssh -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
    set -e
    echo "Setting configuration in docker-compose.yml..."
    sed -i -e "s/<DOCKERTAG>/${docker_tag}/g" docker-compose.yml
    sed -i -e "s/<USER>/${REMOTE_USER}/g" docker-compose.yml
    echo "Setting configuration in nginx.proxy.conf..."
    sed -i -e 's/<LDAP_BASE_DN>/'"\$(grep MONOCLE_LDAP_BASE_DN openldap-env.yaml | cut -d: -f2 | xargs)/g" nginx.proxy.conf
    sed -i -e 's/<LDAP_BIND_DN>/'"\$(grep MONOCLE_LDAP_BIND_DN openldap-env.yaml | cut -d: -f2 | xargs)/g" nginx.proxy.conf
    sed -i -e 's/<LDAP_BIND_PASSWORD>/'"\$(grep MONOCLE_LDAP_BIND_PASSWORD openldap-env.yaml | cut -d: -f2 | xargs)/g" nginx.proxy.conf
    echo "Setting file permissions..."
    chmod 600 docker-compose.yml
    chmod 644 nginx.proxy.conf nginx.ui.conf metadata-api.json
    echo "Pulling ${docker_tag} docker images..."
    docker-compose pull
    echo "Starting containers..."
    docker-compose up -d
    echo "Done."
EOF

# close the connection
ssh -o ControlPath=%C -O exit $REMOTE_USER@$REMOTE_HOST
