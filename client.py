#!/usr/bin/env python3
# -*- coding: utf-8; -*-
'''
Implementacion cliente
'''

import sys
import Ice # pylint: disable=E0401,E0401
Ice.loadSlice('trawlnet.ice')
import TrawlNet # pylint: disable=E0401,C0413

class Client(Ice.Application):
    '''
    Clase cliente
    '''


    def run(self, argv):
        ''' Run '''
        proxy = self.communicator().stringToProxy(argv[1])
        orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxy)
        if not orchestrator:
            raise RuntimeError("Invalid proxy")

        if len(argv) == 2:
            print(orchestrator.getFileList())
            sys.exit
        
        
        
        if len(argv) == 3:
            if not argv[2]:
                raise RuntimeError("Error en la URL")
            if self.is_good_url(argv[2]):
                print(orchestrator.downloadTask(argv[2]))

    def is_good_url(self, url, current=None):
        import re
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return regex.search(url)


sys.exit(Client().main(sys.argv))
