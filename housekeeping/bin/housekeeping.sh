#!/usr/bin/env bash



SERVICE_INSTALL_DIR="$HOME"
# some directories that must be unreadable, so randomly-named links/files cannot be browsed
# for the housekeeping these must be made readable temporarily, then the usual mode restored
# these are the modes:
TEMP_READBLE_DIR_MODE="700"
NORMAL_UNREADBLE_DIR_MODE="331"

NGINX_CONTAINER="proxy"
NGINX_SERVICE_CONF="nginx.proxy.conf"
NGINX_SERVICE_CONF_TEMP_MOVE="${NGINX_SERVICE_CONF}.TEMP_MOVE"
NGINX_MAINTENACE_CONF="nginx.service_maintenance.conf" # returns 503 to all requests

BULK_DOWNLOAD_DIR="${SERVICE_INSTALL_DIR}/monocle_juno_institution_view/downloads/"
BULK_DOWNLOAD_GLOB="*.zip"
BULK_DOWNLOAD_EXPIRY="14"     # age in days when matching files should be deleted

WEB_DOWNLOAD_LINK_DIR="${SERVICE_INSTALL_DIR}/monocle_juno_web_root/downloads/"
WEB_DOWNLOAD_LINK_EXPIRY="30" # age in days when links should be deleted



# disable access to service at proxy
mv "$NGINX_SERVICE_CONF" "$NGINX_SERVICE_CONF_TEMP_MOVE"
cp "$NGINX_MAINTENACE_CONF" "$NGINX_SERVICE_CONF"
docker-compose restart "$NGINX_CONTAINER"

# Delete expired bulk download files
chmod "$TEMP_READBLE_DIR_MODE" "$TEMP_BULK_DOWNLOAD_DIR"
find "$TEMP_BULK_DOWNLOAD_DIR" -name "$BULK_DOWNLOAD_GLOB" -follow -mtime +"$BULK_DOWNLOAD_EXPIRY" -exec rm {} \;
chmod "$NORMAL_UNREADBLE_DIR_MODE" "$TEMP_DOWNLOAD_LINK_DIR"

# Delete expired web download symlinks.
chmod "$TEMP_READBLE_DIR_MODE" "$TEMP_DOWNLOAD_LINK_DIR"
find "$TEMP_DOWNLOAD_LINK_DIR" -type l -mtime +"$WEB_DOWNLOAD_LINK_EXPIRY" -exec rm {} \;
chmod "$NORMAL_UNREADBLE_DIR_MODE" "$TEMP_DOWNLOAD_LINK_DIR"

# reenable access to service at proxy
mv "$NGINX_SERVICE_CONF_TEMP_MOVE" "$NGINX_SERVICE_CONF"
docker-compose restart "$NGINX_CONTAINER"
