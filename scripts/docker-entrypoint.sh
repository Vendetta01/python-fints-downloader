#!/bin/bash

# Exit immediatley if a command exits with a non-zero status.
set -e

# Variables
source /usr/bin/environment.sh


# Source: https://github.com/sameersbn/docker-gitlab/
map_uidgid() {
    USERMAP_ORIG_UID=$(id -u fints)
    USERMAP_ORIG_GID=$(id -g fints)
    USERMAP_NEW_UID=${USERMAP_UID:-$USERMAP_ORIG_UID}
    USERMAP_NEW_GID=${USERMAP_GID:-${USERMAP_ORIG_GID:-$USERMAP_NEW_UID}}
    if [[ ${USERMAP_NEW_UID} != "${USERMAP_ORIG_UID}" || ${USERMAP_NEW_GID} != "${USERMAP_ORIG_GID}" ]]; then
        logit "INFO" "Mapping UID and GID for fints:fints to $USERMAP_NEW_UID:$USERMAP_NEW_GID"
        usermod -u "${USERMAP_NEW_UID}" fints
        groupmod -o -g "${USERMAP_NEW_GID}" fints
    fi
}

set_permissions() {
    # Set permissions for consumption and export directory
    for dir in PAPERLESS_CONSUMPTION_DIR PAPERLESS_EXPORT_DIR; do
      # Extract the name of the current directory from $dir for the error message
      cur_dir_name=$(echo "$dir" | awk -F'_' '{ print tolower($2); }')
      chgrp paperless "${!dir}" || {
          logit "INFO" "Changing group of ${cur_dir_name} directory:"
          logit "INFO" "  ${!dir}"
          logit "INFO" "failed."
          logit "INFO" ""
          logit "INFO" "Either try to set it on your host-mounted directory"
          logit "INFO" "directly, or make sure that the directory has \`g+wx\`"
          logit "INFO" "permissions and the files in it at least \`o+r\`."
      } >&2
      chmod g+wx "${!dir}" || {
          logit "INFO" "Changing group permissions of ${cur_dir_name} directory:"
          logit "INFO" "  ${!dir}"
          logit "INFO" "failed."
          logit "INFO" ""
          logit "INFO" "Either try to set it on your host-mounted directory"
          logit "INFO" "directly, or make sure that the directory has \`g+wx\`"
          logit "INFO" "permissions and the files in it at least \`o+r\`."
      } >&2
    done
    # Set permissions for application directory
    chown -Rh fints:fints /usr/src/fints_downloader
}

migrations() {
    # A simple lock file in case other containers use this startup
    LOCKFILE="/usr/src/fints_downloader/data/db.sqlite3.migration"

    # check for and create lock file in one command 
    if (set -o noclobber; echo "$$" > "${LOCKFILE}") 2> /dev/null
    then
        trap 'rm -f "${LOCKFILE}"; exit $?' INT TERM EXIT
        sudo -HEu fints "python3" "/usr/src/fints_downloader/src/manage.py" "migrate"
        rm ${LOCKFILE}
    fi
}

initialize() {
    map_uidgid
    set_permissions

    # first set up confd itself from env
    logit "INFO" "Setting up confd..."
    /usr/bin/confd -onetime -backend env -confdir /tmp/etc/confd -sync-only

    # Waiting for etcd
    if [[ ${CONF__WAIT_FOR_ETCD__URL+x} ]]; then
        logit "INFO" "Waiting for etcd..."
        /usr/bin/wait-for-it.sh ${CONF__WAIT_FOR_ETCD__URL} -s \
	        -t ${CONF__WAIT_FOR_ETCD__TIME}
    fi

    # now set up all config files initially
    logit "INFO" "Setting up config files"
    #/usr/bin/confd -onetime -confdir /etc/confd \
	#    -config-file /etc/confd/confd.toml -sync-only

    migrations

    touch "$FIRST_START_FILE_URL"
    logit "INFO" "Initialization done"
}


# main
if [[ ! -e "$FIRST_START_FILE_URL" ]]; then
	# Do stuff
	initialize
fi


# Start services
logit "INFO" "Starting supervisord..."
exec /usr/bin/supervisord -c /etc/supervisord.conf

