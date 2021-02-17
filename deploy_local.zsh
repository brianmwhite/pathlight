#!/bin/zsh

git fetch

if [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ]; then
	sudo systemctl stop pathlight
	sudo rm pathlight.pickle

    git pull

    sudo systemctl start pathlight
	journalctl -u pathlight -f
else
    echo "pathlight already up-to-date"
fi
