#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Implementacion del cliente '''

import sys
import Ice # pylint: disable=E0401, C0413
Ice.loadSlice('trawlnet.ice')
import TrawlNet # pylint: disable=E0401, C0413


class Client(Ice.Application):
    ''' Cliente '''

    def run(self, argv):
        ''' Aplicacion de Ice '''
        proxyorc = self.communicator().stringToProxy(argv[1])
        orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxyorc)
        if not orchestrator:
            raise RuntimeError('Error')

        message = orchestrator.downloadTask(argv[2])
        print("Respuesta recibida", message)
        return 0

sys.exit(Client().main(sys.argv))
