#!/usr/bin/env bash

SERVICE_INSTALL_DIR="$HOME"

BULK_DOWNLOAD_DIR="${SERVICE_INSTALL_DIR}/monocle_juno_institution_view/downloads/"
BULK_DOWNLOAD_GLOB="*.zip"
BULK_DOWNLOAD_EXPIRY="14"  # age in days when matching files should be deleted

find "$BULK_DOWNLOAD_DIR" -name "$BULK_DOWNLOAD_GLOB" -follow -mtime +"$BULK_DOWNLOAD_EXPIRY" -exec rm {} \;
