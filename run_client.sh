#!/bin/sh
#

PYTHON=python3

CLIENT_CONFIG=server.config

if [ $# -lt 2 ]; then
  $PYTHON client.py --Ice.Config=$CLIENT_CONFIG "$1"
   exit 0
fi

if [ $# -eq 2 ]; then
  $PYTHON client.py --Ice.Config=$CLIENT_CONFIG "$1" "$2"
fi


