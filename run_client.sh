#!/bin/sh
#

echo "Downloading audio..."
./client.py "$1" "--download" "https://www.youtube.com/watch?v=WVHhayImOOY" \
--Ice.Config=client.config

echo ""
echo "List request..."
./client.py "$1" --Ice.Config=client.config

echo ""
echo "Init transfer..."
./client.py "$1" "--transfer" "Tono de llamada movistar oficial.mp3" \
--Ice.Config=client.config