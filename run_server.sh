#!/bin/sh

echo "Lanzando dowloader y orchestrator"

./downloader.py --Ice.Config=dw.config | tee prxdownloader.out &

sleep 3

./orchestrator.py --Ice.Config=orc.config "$(head -1 prxdownloader.out)"




