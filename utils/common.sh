#!/usr/bin/env bash

function validate_version {
    local VERSION=${1}

    # check semver installed
    hash semver 2>/dev/null
    SEMVER_HASH_STATUS=$?
    if [ "$SEMVER_HASH_STATUS" != "0" ]; then
        echo 'Please install semver by running `yarn global add semver`.'
        exit 1
    fi

    # check valid new version
    # TODO: check valid upgrade from previous
    semver "$VERSION"
    SEMVER_STATUS=$?
    if [ "$SEMVER_STATUS" != "0" ]; then
        echo 'Invalid version. Please follow semver (https://semver.org/).'
        exit 1
    fi
}

function validate_new_version {
    local VERSION=${1}

    # get the latest tags
    git fetch --tags

    # check the version doesn't exist
    if git tag --list | grep -E -q "^${VERSION}$"; then
        echo "Version ${VERSION} already exists."
        exit 1
    fi
}

function validate_environment {
    local ENVIRONMENT=${1}
    if [[ "$ENVIRONMENT" == "prod" || "$ENVIRONMENT" == "dev" ]]; then
        echo "Environment: $ENVIRONMENT"
    else
        echo 'Environment can only be `prod` or `dev`.'
        exit 1
    fi
}

function validate_branch {
    # check branch is master
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$BRANCH" != "master" ]]; then
        echo 'Releases can only be made from `master` branch.'
        exit 1
    fi
}

function validate_staging_empty {
    # check no staged changes
    git diff-index --quiet HEAD --
    STAGING_STATUS=$?
    if [ "$STAGING_STATUS" != "0" ]; then
        echo "Staged changes found. Please commit them separately first."
        exit 1
    fi
}
