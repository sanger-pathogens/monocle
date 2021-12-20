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

RESTART_COUNT=0
MAX_RESTART=10

restart_proxy_container() {
   local LOG_FILE=/tmp/proxy_restart.out
   docker-compose restart "$NGINX_CONTAINER" > "$LOG_FILE" 2>&1
   # if restart fails, attempt restart with the service config NGINX_SERVICE_CONF
   if [ $? != 0 ]; then
      echo "Failed to restart container ${NGINX_CONTAINER}:"
      cat "$LOG_FILE" && rm "$LOG_FILE"
      if [[ RESTART_COUNT -lt MAX_RESTART ]]; then
         echo "Attempting restart with normal service config (${NGINX_SERVICE_CONF})"
         enable_service_access
         RESTART_COUNT=$((RESTART_COUNT+1))
         sleep 10
      fi
      exit 255
   fi
}

disable_service_access() {
   mv "$NGINX_SERVICE_CONF" "$NGINX_SERVICE_CONF_TEMP_MOVE"
   cp "$NGINX_MAINTENACE_CONF" "$NGINX_SERVICE_CONF"
   restart_proxy_container
}

enable_service_access() {
   if [ -f "$NGINX_SERVICE_CONF_TEMP_MOVE" ]; then
      mv "$NGINX_SERVICE_CONF_TEMP_MOVE" "$NGINX_SERVICE_CONF"
      restart_proxy_container
   fi
}

delete_expired_bulk_download_files() {
   chmod "$TEMP_READBLE_DIR_MODE" "$BULK_DOWNLOAD_DIR"
   find "$BULK_DOWNLOAD_DIR" -name "$BULK_DOWNLOAD_GLOB" -follow -mtime +"$BULK_DOWNLOAD_EXPIRY" -exec rm {} \;
   chmod "$NORMAL_UNREADBLE_DIR_MODE" "$BULK_DOWNLOAD_DIR"
}

delete_expired_web_download_links() {
   chmod "$TEMP_READBLE_DIR_MODE" "$WEB_DOWNLOAD_LINK_DIR"
   find "$WEB_DOWNLOAD_LINK_DIR" -type l -mtime +"$WEB_DOWNLOAD_LINK_EXPIRY" -exec rm {} \;
   chmod "$NORMAL_UNREADBLE_DIR_MODE" "$WEB_DOWNLOAD_LINK_DIR"
}


disable_service_access

delete_expired_bulk_download_files

delete_expired_web_download_links

enable_service_access
