#!/bin/sh
# dashcam_launcher.sh

cd /home/madhukar/Desktop/dashcam

# Pull the latest changes from the repository in the current terminal
git pull || true

# Open a new lxterminal and run git pull after a 30-second delay
lxterminal --command="bash -c 'sleep 30; git pull || true'"

# Start the Python script in a new lxterminal
lxterminal --command="python main.py --maxFps=9.0"
