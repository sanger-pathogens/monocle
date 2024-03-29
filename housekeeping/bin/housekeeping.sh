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
# ZIP archives are big, and will be automaticallty recreated as needed, so
# we can delete these quite aggressively
BULK_DOWNLOAD_ZIP_GLOB="*.zip"
BULK_DOWNLOAD_ZIP_EXPIRY="7"
# JSON files hold params for downloads; not too big, and deleting these
# will mean the download link gioven to the user will cease to work,
# so these shouldn't be agressively tidied.
# Note these provide password-less downloads (by design, to enable sharing)
# they shouldn't be left indefinitely.
BULK_DOWNLOAD_JSON_GLOB="*.json"
BULK_DOWNLOAD_JSON_EXPIRY="30"

WEB_DOWNLOAD_LINK_DIR="${SERVICE_INSTALL_DIR}/monocle_web_root/downloads/"
# These are only symlinks so no space issues.
# Note these provide password-less downloads (by design, to enable sharing)
# they shouldn't be left indefinitely.
WEB_DOWNLOAD_LINK_EXPIRY="30"

RESTART_COUNT=0
RESTART_WAIT=10
MAX_RESTART=10

restart_proxy_container() {
   local LOG_FILE=/tmp/proxy_restart.out
   docker-compose restart "$NGINX_CONTAINER" > "$LOG_FILE" 2>&1
   # if restart fails, attempt restart with the service config NGINX_SERVICE_CONF
   if [ $? != 0 ]; then
      echo "Failed to restart container ${NGINX_CONTAINER}:"
      cat "$LOG_FILE" && rm "$LOG_FILE"
      RESTART_COUNT=$((RESTART_COUNT+1))
      if [[ RESTART_COUNT -lt $((MAX_RESTART+1)) ]]; then
         echo "Will attempting restart ${RESTART_COUNT}/${MAX_RESTART} with normal service config (${NGINX_SERVICE_CONF}) in ${RESTART_WAIT} seconds"
         sleep "$RESTART_WAIT"
         restart_proxy_container
      else
         echo "Restart limit reached"
         exit 255
      fi
   else
      if [[ RESTART_COUNT -gt 0 ]]; then
         echo "Successfully restarted container ${NGINX_CONTAINER} at attempt ${RESTART_COUNT}."
      fi
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
   find "$BULK_DOWNLOAD_DIR" -name "$BULK_DOWNLOAD_ZIP_GLOB"  -follow -mtime +"$BULK_DOWNLOAD_ZIP_EXPIRY"  -exec rm {} \;
   find "$BULK_DOWNLOAD_DIR" -name "$BULK_DOWNLOAD_JSON_GLOB" -follow -mtime +"$BULK_DOWNLOAD_JSON_EXPIRY" -exec rm {} \;
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
