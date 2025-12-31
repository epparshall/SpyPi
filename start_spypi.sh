#!/bin/bash
# This script is designed to run the SpyPi.py script on boot.
# Make sure to place this script in a location that your cron job can access.
# The path to the SpyPi project directory is hardcoded here.
# You may need to change this path if you move the project.
cd /Users/evanparshall/Github/SpyPi
python SpyPi.py
