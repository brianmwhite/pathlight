#!/bin/zsh
sudo systemctl stop pathlight
sudo rm pathlight.pickle

git reset --hard master@{1}

sudo systemctl start pathlight
journalctl -u pathlight -f
