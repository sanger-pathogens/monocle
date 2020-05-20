#!/usr/bin/env bash

# Make a release of Monocle.

VERSION=$1
# check args count
if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

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

# check branch is master
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "master" ]]; then
  echo 'Releases can only be made from `master` branch.'
  exit 1
fi

# get the latest tags
git fetch --tags

# check the version doesn't exist
if git tag --list | grep -E -q "^${VERSION}$"; then
  echo "Version ${VERSION} already exists."
  exit 1
fi

# check no staged changes
if git diff --cached --exit-code; then
  echo "Staged changes found. Please commit them separately first."
  exit 1
fi

echo "Creating version ${VERSION}..."

# TODO: check tests are passing

# tag and commit
git commit -m "v${VERSION}"
git tag "v${VERSION}"

# make sure origin is up to date
git push origin master
git push origin "v${VERSION}"
