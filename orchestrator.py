#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Orchestrator '''
import sys
import Ice # pylint: disable=E0401, C0413
Ice.loadSlice('trawlnet.ice')
import TrawlNet # pylint: disable=E0401, C0413

class Orchestrator(TrawlNet.Orchestrator):

    ''' Orchestrator class '''
    def downloadTask(self, url, current=None):
        ''' download task '''
        print("Procesando la url en el orchestrator...")
        print(url)
        print("Enviando la peticion al Downloader...")
        response = self.downloader.addDownloadTask(url)
        print("Se ha recibido una respuesta ", response)
        return response

    def __init__(self, download):
        ''' builder '''
        self.downloader = download


class Server(Ice.Application):
    ''' Server '''

    def run(self, argv):
        ''' init server '''
        broker = self.communicator()
        prx_downloader = broker.stringToProxy(argv[1])
        downloader = TrawlNet.DownloaderPrx.checkedCast(prx_downloader)
        serv_orc = Orchestrator(downloader)
        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        proxy_orc = adapter.add(serv_orc, broker.stringToIdentity("orchestrator"))
        print(proxy_orc)
        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
