#!/bin/sh
# dashcam_launcher.sh

cd /home/madhukar/Desktop/dashcam

# Pull the latest changes from the repository
lxterminal --command="git pull || true"

lxterminal --command="python main.py --maxFps=3.0"
