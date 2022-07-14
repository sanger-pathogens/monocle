#!/usr/bin/env bash

# Deploy a code/database Monocle release.
# The version number provided is expected to be without the leading v, e.g. 0.1.26

set -e

ECHO_EM=$(tput bold)
ECHO_RESET=$(tput sgr0)

usage_summary() {
  echo "${ECHO_EM}Usage:${ECHO_RESET}
  
$0 \\
   --env  (dev|prod) \\
   --host <deploy host> \\
   --user <deploy username> \\
   (--version <version number>|--branch <branch>|--commit <sha-1>) \\
   [options]"
}

usage() {
   usage_summary
   echo "
For more help:

$0 --help"
   exit 1
}

help() {
  usage_summary
  echo "
${ECHO_EM}Mandatory arguments:${ECHO_RESET}
-e --env    deployed environment: \`prod\` or \`dev\`
-u --user   username on deployment host
-h --host   deployment host name or IP address

${ECHO_EM}Additionally, exactly one of the following is mandatory:${ECHO_RESET}
-v --version   version number (without \`v\` prefix): will deploy this git tag
               from the repo, and docker images with matching tags
-b --branch    branch name: deploy the HEAD of this branch in the repo, and the
               docker images build from the HEAD of the branch (using the
               \`commit-<short_hash>\` docker tag, where \`<short_hash>\` is the
               first 8 characters of the SHA-1 hash of the HEAD commit)
               ${ECHO_EM}May not be used when --mode is \`database\` or \`all\`${ECHO_RESET}
-s --commit    SHA-1 hash:  deploy this commit from the repo, and the docker
               images build from that commit  (using the \`commit-<short_hash>\`
               docker tag, where \`<short_hash>\` is the first 8
               characters of the SHA-1 hash)
               ${ECHO_EM}May not be used when --mode is \`database\` or \`all\`${ECHO_RESET}

${ECHO_EM}Required environment variables:${ECHO_RESET}
Environment variables GITLAB_USER and GITLAB_TOKEN must be set if new docker
images are being deployed to the host.  These must be a username and access
token with permission to read the sanger-pathogens/monocle repo.

${ECHO_EM}Options:${ECHO_RESET}

-m --mode      deploy mode: \`application\` (default: deploy app code and config
               only), \`database\` (deploy database release only) or \`all\`
               (deploy app and database release)
-c --conn-file ${ECHO_EM}FULL${ECHO_RESET} path to database connection file, required for a database
               release
-p --port      port number for deployment host

For a database release, the script expects to find a release.sql file under
the database/releases/<version|tag> folder.

Example 1: deploy v0.1.45 of the application to dev instance and run the
associated database release using the \`db.cnf\` connection file in the
working directory:
${ECHO_EM}$0 --env dev --host monocle_vm.dev.pam.sanger.ac.uk --user monocle\\
   --version 0.1.45 \\
   --mode all --conn-file \$(pwd)/db.cnf${ECHO_RESET}

Example 2: deploy only the 0.1.45 database release, without changes to the app,
using the \`db.cnf\` connection file in the working directory:
${ECHO_EM}$0 --env dev --host monocle_vm.dev.pam.sanger.ac.uk --user monocle \\
   --version 0.1.45 \\
   --mode database --conn-file \$(pwd)/db.cnf${ECHO_RESET}

Example 3: deploy HEAD of master branch (pre-release) application to an
instance on your local dev machine:
${ECHO_EM}$0 --env dev --host localhost --user dev_username \\
   --branch master${ECHO_RESET}
   
Example 4: deploy app from feature branch \`feature/something_new\` to an
instance on your local dev machine:
${ECHO_EM}$0 --env dev --host localhost --user dev_username \\
   --branch feature/something_new${ECHO_RESET}

Example 5: deploy app from commit \`a1b2c3d4\` to an instance on your local
dev machine:
${ECHO_EM}$0 --env dev --host localhost --user dev_username \\
   --branch feature/something_new${ECHO_RESET}"
  exit
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
BRANCH=
COMMIT=
REMOTE_USER=
REMOTE_HOST=
SSH_PORT_ARG=
db_release_file=
FAILED_CODE=2

deploy_mode_application="application"
deploy_mode_database="database"
deploy_mode_all="all"
DEPLOY_MODE="${deploy_mode_application}"

# read command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case "$key" in
      --help)
      help
      ;;
    
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

      # Assignment to `SCP_PORT_ARG` and `SSH_PORT_ARG` uses the standart parameter expansion of the form
      # `${var:+word}`, where the expression is expanded to `word` only if `var` isn't unset or null (see
      # https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_06_02)
      -p|--port)
      shift
      SSH_PORT_ARG=${1:+-p "$1"}
      SCP_PORT_ARG=${1:+-P "$1"}
      ;;
      -p=*|--port=*)
      SSH_PORT_ARG=${"${key#*=}":+-p "${key#*=}"}
      SCP_PORT_ARG=${"${key#*=}":+-P "${key#*=}"}
      ;;

      -m|--mode)
      shift
      DEPLOY_MODE="$1"
      ;;
      -m=*|--mode=*)
      DEPLOY_MODE="${key#*=}"
      ;;

      -b|--branch)
      shift
      BRANCH="$1"
      ;;
      -b=*|--branch=*)
      BRANCH="${key#*=}"
      ;;

      -s|--commit)
      shift
      COMMIT="$1"
      ;;
      -s=*|--commit=*)
      COMMIT="${key#*=}"
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
if  [[ -z "${ENVIRONMENT}" ]] || [[ -z "${REMOTE_USER}" ]] || [[ -z "${REMOTE_HOST}" ]]
then
    usage
fi

# only specifify ONE of version, branch or commit
num=0
if [[ ! -z "${VERSION}" ]]; then ((++num)); fi
if [[ ! -z "${BRANCH}" ]]; then ((++num)); fi
if [[ ! -z "${COMMIT}" ]]; then ((++num)); fi
if ((num != 1))
then
   echo "${ECHO_EM}Use only one of --version, --branch or --commit${ECHO_RESET}
"
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
if [[ "${DEPLOY_MODE}" == "${deploy_mode_all}" || "${DEPLOY_MODE}" == "${deploy_mode_database}" ]]
then
   if [[ -z "${VERSION}" ]]
   then
      echo "${ECHO_EM}\`--mode ${DEPLOY_MODE}\` can only be used with the \`--version\` option${ECHO_RESET}
"
      usage
   fi
   if [[ ! -f "${DB_CONNECTION_FILE}" ]]
   then
      echo "${ECHO_EM}Unable to find database connection file: '${DB_CONNECTION_FILE}'.  Note: the full path must be provided!${ECHO_RESET}
"
      usage
   fi
fi

# pull the required git tag, branch or commit, and work out the docker tag required
docker_tag=
deploy_dir=$(mktemp -d -t monocle-XXXXXXXXXX)
git clone git@gitlab.internal.sanger.ac.uk:sanger-pathogens/monocle.git ${deploy_dir}
cd ${deploy_dir}
trap "{ if [[ -d ${deploy_dir} ]]; then rm -rf ${deploy_dir}; fi }" EXIT
if [[ ! -z "$VERSION" ]]; then
   git checkout "tags/v${VERSION}"
   docker_tag="v${VERSION}"
   echo "${ECHO_EM}Deploying tag v${VERSION} with docker images tagged ${docker_tag}${ECHO_RESET}"
elif [[ ! -z "$BRANCH" ]]; then
   git checkout "$BRANCH"
   docker_tag="commit-$(git rev-parse --short=8 HEAD)"
   echo "${ECHO_EM}Deploying branch ${BRANCH} with docker images tagged ${docker_tag}${ECHO_RESET}"
elif [[ ! -z "$COMMIT" ]]; then
   git checkout "$COMMIT"
   docker_tag="commit-$(git rev-parse --short=8 HEAD)"
   echo "${ECHO_EM}Deploying commit ${COMMIT} with docker images tagged ${docker_tag}${ECHO_RESET}"
else # this should be unreachable if option validation was done correctly
   echo "${ECHO_EM}Must provide --version, --branch or --commit${ECHO_RESET}
"
   usage
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
    db_release_file="./database/releases/${VERSION}/release.sql"
    run_db_release_checks "${db_release_file}"
fi

# shut down applications first
# keep connection to avoid multiple password entries
ssh -o ControlMaster=yes -o ControlPersist=yes -o ControlPath=%C $SSH_PORT_ARG $REMOTE_USER@$REMOTE_HOST << EOF
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
    echo "${ECHO_EM}Database release ${VERSION} completed successfully${ECHO_RESET}"
fi

if [[ "${DEPLOY_MODE}" == "${deploy_mode_all}" || "${DEPLOY_MODE}" == "${deploy_mode_application}" ]]
then

    if [ -z ${GITLAB_USER+x} ]
    then
      echo Please set your gitlab login into variable GITLAB_USER
      exit 1
    fi
    if [ -z ${GITLAB_TOKEN+x} ]
    then
      echo Please set your personal token into variable GITLAB_TOKEN
      exit 1
    fi

    # copy production compose file (template)
    scp -o ControlPath=%C $SCP_PORT_ARG docker-compose.prod.yml $REMOTE_USER@$REMOTE_HOST:~/docker-compose.yml

    # copy production nginx config
    # (may want to remove from git long term)
    scp -o ControlPath=%C $SCP_PORT_ARG proxy/nginx.prod.proxy.conf           $REMOTE_USER@$REMOTE_HOST:~/nginx.proxy.conf
    scp -o ControlPath=%C $SCP_PORT_ARG proxy/nginx.service_maintenance.conf  $REMOTE_USER@$REMOTE_HOST:~/nginx.service_maintenance.conf

    # scripts for syncing sample data view
    scp -o ControlPath=%C $SCP_PORT_ARG data_view/bin/create_download_view_for_sample_data.py $REMOTE_USER@$REMOTE_HOST:~/create_download_view_for_sample_data.py
    scp -o ControlPath=%C $SCP_PORT_ARG data_view/bin/run_data_view_script_in_docker.sh       $REMOTE_USER@$REMOTE_HOST:~/run_data_view_script_in_docker.sh
    
    # hopusekeeping script(s)
    scp -o ControlPath=%C $SCP_PORT_ARG housekeeping/bin/housekeeping.sh $REMOTE_USER@$REMOTE_HOST:~/housekeeping.sh


    # replace the running version
    # using existing connection
    # note: local variables are substituted as normal,
    #       remote variables need escaping
    #       (eg. VERSION vs API_SECRET_KEY)
    ssh -o ControlPath=%C $SSH_PORT_ARG $REMOTE_USER@$REMOTE_HOST << EOF
        set -e
        echo "Setting configuration in docker-compose.yml..."
        sed -i -e "s/<DOCKERTAG>/${docker_tag}/g" docker-compose.yml run_data_view_script_in_docker.sh
        sed -i -e "s/<USER>/${REMOTE_USER}/g"     docker-compose.yml run_data_view_script_in_docker.sh
        sed -i -e "s/<USER_UID>/\$(id -u)/g"      docker-compose.yml
        sed -i -e "s/<USER_GID>/\$(id -g)/g"      docker-compose.yml
        echo "Setting configuration in nginx.proxy.conf..."
        sed -i -e 's/<LDAP_BASE_DN>/'"\$(grep MONOCLE_LDAP_BASE_DN openldap-env.yaml | cut -d: -f2 | xargs)/g"             nginx.proxy.conf
        sed -i -e 's/<LDAP_BIND_DN>/'"\$(grep MONOCLE_LDAP_BIND_DN openldap-env.yaml | cut -d: -f2 | xargs)/g"             nginx.proxy.conf
        sed -i -e 's/<LDAP_BIND_PASSWORD>/'"\$(grep MONOCLE_LDAP_BIND_PASSWORD openldap-env.yaml | cut -d: -f2 | xargs)/g" nginx.proxy.conf
        echo "Setting file permissions..."
        chmod 600 docker-compose.yml
        chmod 644 nginx.proxy.conf nginx.service_maintenance.conf
        chmod 700 create_download_view_for_sample_data.py run_data_view_script_in_docker.sh housekeeping.sh
        echo "Pulling ${docker_tag} docker images..."
        echo "${GITLAB_TOKEN}" | docker login -u "${GITLAB_USER}" --password-stdin "gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle"
        docker-compose pull
        docker logout "gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle"
EOF
fi

# restart the application docker containers
ssh -o ControlPath=%C $SSH_PORT_ARG $REMOTE_USER@$REMOTE_HOST << EOF
    set -e
    echo "Starting containers..."
    docker-compose up -d
    echo "Done."
EOF

# close the connection
ssh -o ControlPath=%C -O exit $SSH_PORT_ARG $REMOTE_USER@$REMOTE_HOST
