#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('trawlnet.ice')
import TrawlNet


class Client(Ice.Application):
    def __init__(self):
        print('Cliente iniciado\n')
    def run(self, argv):
        proxyorc = self.communicator().stringToProxy(argv[1])
        orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxyorc)
        if not orchestrator:
            raise RuntimeError('Error')

        message = orchestrator.downloadTask(argv[2])
        print("Respuesta recibida",message )


        return 0

sys.exit(Client().main(sys.argv))
