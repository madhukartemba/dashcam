#!/bin/sh
# dashcam_launcher.sh

cd /home/madhukar/Desktop/dashcam

# Pull the latest changes from the repository
git pull || true

lxterminal --command="python main.py --maxFps=2.0 --showPreview=false"