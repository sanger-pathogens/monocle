#!/usr/bin/env bash

# Deploy a code/database Monocle release.
# The version number provided is expected to be without the leading v, e.g. 0.1.26

usage() {
  echo "Usage: $0 arguments [options]
       
       Mandatory arguments:
       -e --env         deployed environment: \`prod\` or \`dev\`
       -u --user        user id on deployment host
       -h --host        deployment host name or IP address

       Options:
       -v --version     version number without \`v\` prefix
                        IMPORTANT: if this is not provided, then both
                        \`--branch\` and \`--tag\` must be specified
       -m --mode        deploy mode - \`application\` (default), \`database\` or \`all\`
                        - deploy a code version [only], database version [only]
                          or code AND database version
       -d --domain      service domain name; overrides the default based on
                        the deployed environment (set by \`--env\`)
       -b --branch      deploy from this branch instead of git tag derived
                        from version number (set by \`--version\`)
       -t --tag         docker images tag; overrides tag derived from version
                        number (set by \`--version\`)
       -c --conn-file   a database connection file, required for a database release

       (There is no option to set the public domain for the service, as
       that feature is reserved for the production environment.)

       For a database release, the script expects to find a release.sql file under
       the database/releases/<version|tag> folder.

       Example 1: deploy code to pathogens_dev instance and run the associated database release
                  using the db.cnf connection file:
       $0 -e dev -v 0.1.45 -m all -u ubuntu -h monocle_vm.dev.pam.sanger.ac.uk -c ~/db.cnf
          
       Example 2: deploy unstable (pre-release) code version as \`dev_user@localhost\`
       $0 -e dev -u dev_user -h localhost --domain localhost --branch master --tag unstable
          
       Example 3: deploy as \`dev_user@localhost\`, from feature branch
                  \`some_feature_branch\`, using docker images built from
                  commit \`ae48f554\`:
       $0 -e dev -u dev_user -h localhost --domain localhost --branch some_feature_branch --tag commit-ae48f554

       Example 4: deploy only the 0.1.45 database release using a db.cnf database connection file:
       $0 -e dev -v 0.1.45 -m database -u ubuntu -h monocle_vm.dev.pam.sanger.ac.uk -c ~/db.cnf
"
  exit 1
}

# run some basic checks for a database release
run_db_release_checks() {
    local release_sql_file=$1

    local release_aborted_message="Release aborted - no changes have been applied"
    local db_release_info_message="If you do not need a database release, then omit the '-m' and '-c' arguments"

    # the user must have access to a local mysql client for database releases
    which mysql 2>&1 > /dev/null && mysql --version 2>&1 > /dev/null
    if [[ $? -ne 0 ]]
    then
        echo "${ECHO_EM}FATAL ERROR: Please install a mysql client for database releases${ECHO_RESET}"
        echo "${ECHO_EM}${release_aborted_message}${ECHO_RESET}"
        echo "${ECHO_EM}${db_release_info_message}${ECHO_RESET}"
        exit ${FAILED_CODE}
    fi

    # check the database release file exists
    if [[ ! -f "${release_sql_file}" ]]
    then
        echo "${ECHO_EM}FATAL ERROR: Unable to find the database release file: ${release_sql_file}${ECHO_RESET}"
        echo "${ECHO_EM}${release_aborted_message}${ECHO_RESET}"
        echo "${ECHO_EM}${db_release_info_message}${ECHO_RESET}"
        exit ${FAILED_CODE}
    fi

    echo "${ECHO_EM}Using database release file: ${release_sql_file}${ECHO_RESET}"
}

ENVIRONMENT=
VERSION=
REMOTE_USER=
REMOTE_HOST=
db_release_file=
FAILED_CODE=2

deploy_mode_application="application"
deploy_mode_database="database"
deploy_mode_all="all"
DEPLOY_MODE="${deploy_mode_application}"

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

      -m|--mode)
      shift
      DEPLOY_MODE="$1"
      ;;
      -m=*|--mode=*)
      DEPLOY_MODE="${key#*=}"
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

      -c|--conn-file)
      shift
      DB_CONNECTION_FILE="$1"
      ;;
      -c=*|--conn-file=*)
      DB_CONNECTION_FILE="${key#*=}"
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
    [[ -z "${REMOTE_USER}" ]] || [[ -z "${REMOTE_HOST}" ]]
then
    usage
fi

# check the deploy mode
if [[ "${DEPLOY_MODE}" != "${deploy_mode_all}" ]] &&
   [[ "${DEPLOY_MODE}" != "${deploy_mode_database}" ]] &&
   [[ "${DEPLOY_MODE}" != "${deploy_mode_application}" ]]
then
    echo "${ECHO_EM}Illegal mode argument: '${DEPLOY_MODE}'${ECHO_RESET}"
    usage
fi

# database release specific checks
if [[ "${DEPLOY_MODE}" == "${deploy_mode_all}" || "${DEPLOY_MODE}" == "${deploy_mode_database}" ]] &&
   [[ ! -f "${DB_CONNECTION_FILE}" ]]
then
    echo "${ECHO_EM}Unable to find database connection file: '${DB_CONNECTION_FILE}'${ECHO_RESET}"
    usage
fi

# if no version, then branch and tag must be specified
if [[ -z "${VERSION}" ]] && [[ -z "${OPT_BRANCH}" || -z "${OPT_TAG}" ]]
then
   echo "${ECHO_EM}When not using --version, --branch and --tag must both be provided${ECHO_RESET}"
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
db_release_tag="${VERSION}"
if [[ ! -z "$OPT_TAG" ]]; then
   echo "${ECHO_EM}Using docker images with tag ${OPT_TAG} in place of version number tag${ECHO_RESET}"
   docker_tag="$OPT_TAG"
   db_release_tag="$OPT_TAG"
fi

# validate input args
source "${deploy_dir}/utils/common.sh"
validate_environment "${ENVIRONMENT}"
if [[ ! -z "${VERSION}" ]]; then
   validate_version "${VERSION}"
fi

# do we need to setup for a database release...
if [[ "${DEPLOY_MODE}" == "${deploy_mode_all}" || "${DEPLOY_MODE}" == "${deploy_mode_database}" ]]
then
    db_release_file="./database/releases/${db_release_tag}/release.sql"
    run_db_release_checks "${db_release_file}"
fi

# shut down applications first
# keep connection to avoid multiple password entries
ssh -o ControlMaster=yes -o ControlPersist=yes -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
    set -e
    echo "Stopping existing containers..."
    docker-compose down
EOF

# perform the database release (if required)
if [[ "${DEPLOY_MODE}" == "${deploy_mode_all}" || "${DEPLOY_MODE}" == "${deploy_mode_database}" ]]
then
    mysql --defaults-file="${DB_CONNECTION_FILE}" < "${db_release_file}"
    db_release_status=$?
    if [[ ${db_release_status} -ne 0 ]]
    then
        echo "${ECHO_EM}FATAL ERROR: Database release ${db_release_file} failed${ECHO_RESET}"
        echo "${ECHO_EM}Mysql client returned error status ${db_release_status}${ECHO_RESET}"
        exit ${FAILED_CODE}
    fi
    echo "${ECHO_EM}Database release ${db_release_tag} completed successfully${ECHO_RESET}"
fi

if [[ "${DEPLOY_MODE}" == "${deploy_mode_all}" || "${DEPLOY_MODE}" == "${deploy_mode_application}" ]]
then
    # copy production compose file (template)
    scp -o ControlPath=%C docker-compose.prod.yml $REMOTE_USER@$REMOTE_HOST:~/docker-compose.yml

    # copy production nginx config (for proxy and ui), metadata api config
    # (may want to remove from git long term)
    scp -o ControlPath=%C proxy/nginx.prod.proxy.conf  $REMOTE_USER@$REMOTE_HOST:~/nginx.proxy.conf
    scp -o ControlPath=%C ui/nginx.prod.ui.conf        $REMOTE_USER@$REMOTE_HOST:~/nginx.ui.conf
    scp -o ControlPath=%C metadata/juno/config.json    $REMOTE_USER@$REMOTE_HOST:~/metadata-api.json

    # scripts for syncing sample data view
    scp -o ControlPath=%C data_view/bin/create_download_view_for_sample_data.py $REMOTE_USER@$REMOTE_HOST:~/create_download_view_for_sample_data.py
    scp -o ControlPath=%C data_view/bin/run_data_view_script_in_docker.sh       $REMOTE_USER@$REMOTE_HOST:~/run_data_view_script_in_docker.sh
    
    # replace the running version
    # using existing connection
    # note: local variables are substituted as normal,
    #       remote variables need escaping
    #       (eg. VERSION vs API_SECRET_KEY)
    ssh -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
        set -e
        echo "Setting configuration in docker-compose.yml..."
        sed -i -e "s/<DOCKERTAG>/${docker_tag}/g" docker-compose.yml run_data_view_script_in_docker.sh
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
EOF
fi

# restart the application docker containers
ssh -o ControlPath=%C $REMOTE_USER@$REMOTE_HOST << EOF
    set -e
    echo "Starting containers..."
    docker-compose up -d
    echo "Done."
EOF

# close the connection
ssh -o ControlPath=%C -O exit $REMOTE_USER@$REMOTE_HOST
