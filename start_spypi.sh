#!/bin/bash
# This script is designed to run the SpyPi.py script on boot.
# It navigates to the directory where this script is located, making it portable.
cd "$(dirname "$0")"
python SpyPi.py
