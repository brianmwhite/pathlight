#!/bin/zsh

git fetch

if [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ]; then
	systemctl stop pathlight
	rm pathlight.pickle

    git pull

    systemctl start pathlight
	journalctl -u pathlight -f
else
    echo "pathlight already up-to-date"
fi
