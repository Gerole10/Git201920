#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

import sys
import Ice
Ice.loadSlice('trawlnet.ice')
import TrawlNet

class Downloader(TrawlNet.Downloader):
    def addDownloadTask(self, url, current=None):
        print("Se ha recibido la url con éxito: ",url)
        print("Descargando...",url)
        # Descargaremos algo de youtube

        return "Descarga finalizada"
