#!/usr/bin/bash
systemctl stop pathlight
rm pathlight.pickle

git reset --hard master@{1}

systemctl start pathlight
journalctl -u pathlight -f
