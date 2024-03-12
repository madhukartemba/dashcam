#!/bin/sh
# dashcam_launcher.sh

sudo systemctl stop isc-dhcp-server

cd /home/madhukar/Desktop/dashcam

# Pull the latest changes from the repository
git pull || true

sudo systemctl start isc-dhcp-server

lxterminal --command="python main.py --maxFps=2.1"
