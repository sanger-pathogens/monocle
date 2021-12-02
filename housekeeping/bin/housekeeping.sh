#!/usr/bin/env bash

SERVICE_INSTALL_DIR="$HOME"
UNREADBLE_DIR_MODE="331" # for directories that must be unreadable so randomly-named links/files cannot be browsed

BULK_DOWNLOAD_DIR="${SERVICE_INSTALL_DIR}/monocle_juno_institution_view/downloads/"
TEMP_BULK_DOWNLOAD_DIR="${SERVICE_INSTALL_DIR}/temp_bulk_downloads/"
BULK_DOWNLOAD_GLOB="*.zip"
BULK_DOWNLOAD_EXPIRY="14"     # age in days when matching files should be deleted

WEB_DOWNLOAD_LINK_DIR="${SERVICE_INSTALL_DIR}/monocle_juno_web_root/downloads/"
TEMP_DOWNLOAD_LINK_DIR="${SERVICE_INSTALL_DIR}/temp_web_downloads/"
WEB_DOWNLOAD_LINK_EXPIRY="30" # age in days when links should be deleted


# Delete expired bulk download files
# Note the bulk downloads directory is moved (to a location inaccessible via the web) and made readable to do the cleanup.
# Moving it back is conditional on the chmod restoring the correct mode for the web-accessible location.
mv "$BULK_DOWNLOAD_DIR" "$TEMP_BULK_DOWNLOAD_DIR"
chmod 700 "$TEMP_BULK_DOWNLOAD_DIR"
find "$TEMP_BULK_DOWNLOAD_DIR" -name "$BULK_DOWNLOAD_GLOB" -follow -mtime +"$BULK_DOWNLOAD_EXPIRY" -exec rm {} \;
chmod "$UNREADBLE_DIR_MODE" "$TEMP_DOWNLOAD_LINK_DIR" && mv "$TEMP_BULK_DOWNLOAD_DIR" "$BULK_DOWNLOAD_DIR"


# Delete expired web download symlinks.
# Note the download symlinks directory is moved (to a location inaccessible via the web) and made readable to do the cleanup.
# Moving it back is conditional on the chmod restoring the correct mode for the web-accessible location.
mv "$WEB_DOWNLOAD_LINK_DIR" "$TEMP_DOWNLOAD_LINK_DIR"
chmod 700 "$TEMP_DOWNLOAD_LINK_DIR"
find "$TEMP_DOWNLOAD_LINK_DIR" -type l -mtime +"$WEB_DOWNLOAD_LINK_EXPIRY" -exec rm {} \;
chmod "$UNREADBLE_DIR_MODE" "$TEMP_DOWNLOAD_LINK_DIR" && mv "$TEMP_DOWNLOAD_LINK_DIR" "$WEB_DOWNLOAD_LINK_DIR"
