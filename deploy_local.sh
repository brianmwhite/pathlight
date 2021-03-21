#!/usr/bin/bash

SERVICENAME="pathlight"
DELETEPICKLE=false

git fetch

if [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ]; then

    while true; do
        read -p "Delete saved[pickle] data? [yN] " yn
        case $yn in
            [Yy]* ) DELETEPICKLE=true; break;;
            [Nn]* ) DELETEPICKLE=false; break;;
            * ) DELETEPICKLE=false; break;;
        esac
    done

    echo "stopping $SERVICENAME service"
    sudo systemctl stop $SERVICENAME

    if [ "$DELETEPICKLE" = true ] ; then
        echo "deleting $SERVICENAME.pickle file"
        rm $SERVICENAME.pickle
    fi

    echo "updating code from repo"
    git pull

    echo "starting $SERVICENAME service"
    sudo systemctl start $SERVICENAME

    echo "viewing logs for $SERVICENAME service"
	journalctl -u $SERVICENAME -f
else
    echo "$SERVICENAME already up-to-date"
fi
