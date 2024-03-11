#!/bin/sh
# dashcam_launcher.sh

sleep 5

sudo systemctl stop isc-dhcp-server
sudo systemctl start isc-dhcp-server

sleep 5

cd /home/madhukar/Desktop/dashcam

# Pull the latest changes from the repository
git pull || true

lxterminal --command="python main.py --maxFps=2.1 --showPreview=false"
