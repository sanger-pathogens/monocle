#!/usr/bin/env bash

SERVICE_INSTALL_DIR="$HOME"

BULK_DOWNLOAD_DIR="${SERVICE_INSTALL_DIR}/monocle_juno_institution_view/downloads/"
BULK_DOWNLOAD_GLOB="*.zip"
BULK_DOWNLOAD_EXPIRY="14"  # age in days when matching files should be deleted

WEB_DOWNLOAD_LINK_DIR="${SERVICE_INSTALL_DIR}/monocle_juno_web_root/downloads/"
TEMP_DOWNLOAD_LINK_DIR="${SERVICE_INSTALL_DIR}/temp_web_downloads/"
WEB_DOWNLOAD_LINK_EXPIRY="30"     # age in days when links should be deleted
WEB_DOWNLOAD_LINK_DIR_MODE="331"  # directory must be unreadable so the randomly-named links cannot be browsed

# Delete expired bulk download files
find "$BULK_DOWNLOAD_DIR" -name "$BULK_DOWNLOAD_GLOB" -follow -mtime +"$BULK_DOWNLOAD_EXPIRY" -exec rm {} \;

# Delete expired web download symlinks.
# The web download directory must be unreadable at all times, so that downlaod are 
# only possible with prior knowledge of the random link name  (i.e. users must not 
# be able to see other link names in their browser). => we need to move the 
# directory temporarily and make it readable before doing the clean up.  We 
# **MUST** restore the correct mode before moving it back to the proper location! 
# This will make download impossible for a second or two whilst this job runs.
mv "$WEB_DOWNLOAD_LINK_DIR" "$TEMP_DOWNLOAD_LINK_DIR"
chmod 700 "$TEMP_DOWNLOAD_LINK_DIR"
find "$TEMP_DOWNLOAD_LINK_DIR" -type l -mtime +"$WEB_DOWNLOAD_LINK_EXPIRY" -exec rm {} \;
chmod "$WEB_DOWNLOAD_LINK_DIR_MODE" "$TEMP_DOWNLOAD_LINK_DIR"
mv "$TEMP_DOWNLOAD_LINK_DIR" "$WEB_DOWNLOAD_LINK_DIR"
