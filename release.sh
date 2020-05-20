#!/usr/bin/env bash

# Make a release of Monocle.

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/utils/common.sh"

# check args count
if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION=$1
validate_version "${VERSION}"
validate_branch
validate_staging_empty

# TODO: check tests are passing

# tag and commit
echo "Creating version ${VERSION}..."
git commit -m "v${VERSION}"
git tag "v${VERSION}"

# make sure origin is up to date
echo "Pushing version ${VERSION}..."
git push origin master
git push origin "v${VERSION}"

echo "Done."