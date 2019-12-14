#!/bin/sh



rm -r IceStorm/
mkdir -p IceStorm/

echo "Run icebox"
sudo icebox --Ice.Config=icebox.config &

sleep 2
echo "Run downloaders"
./downloader.py --Ice.Config=dw.config | tee proxydw.out &

sleep 2

echo "Run orchestrators"
./orchestrator.py --Ice.Config=orc.config "$(head -1 proxydw.out)" &

sleep 2

./orchestrator.py --Ice.Config=orc.config "$(head -1 proxydw.out)"
