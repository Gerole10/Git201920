 #!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

import re
import sys
import Ice # pylint: disable=E0401
import IceStorm
Ice.loadSlice('trawlnet.ice')
import TrawlNet # pylint: disable=E0401,C0413

class Server(Ice.Application):  #pylint: disable=R0903
    '''
    Servidor
    '''
    def run(self, argv):
        '''
        Init
        '''
        key = 'IceStorm.TopicManager.Proxy'
        topic_name_file = "UpdateEvents"
        topic_name_orchestrator = "OrchestratorSync"
        broker = self.communicator()
        proxy = broker.propertyToProxy(key)
        if proxy is None:
            return None
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(proxy) # pylint: disable=E1101
        if not topic_mgr:
            return 2
     
        try:
            topic_update = topic_mgr.retrieve(topic_name_file)
        except IceStorm.NoSuchTopic: # pylint: disable=E1101
            topic_update = topic_mgr.create(topic_name_file)

        try:
            topic_orchestrator = topic_mgr.retrieve(topic_name_orchestrator)
        except IceStorm.NoSuchTopic: # pylint: disable=E1101
            topic_orchestrator = topic_mgr.create(topic_name_orchestrator)

        IniciarOrchestrator(broker, argv[1], topic_update, topic_orchestrator)
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

    
class OrchestratorEventI(TrawlNet.OrchestratorEvent):
    '''
    OrchestratorEventI
    '''
    orchestrator = None

    def hello(self, orchestrator, current=None):
        ''' HELLO '''
        if self.orchestrator:
            self.orchestrator.saludar(orchestrator)

class OrchestratorI(TrawlNet.Orchestrator):
    '''
    OrchestratorI
    '''
    orchestrator = None

    def announce(self, orchestrator, current=None):
        ''' Announce '''
        if self.orchestrator:
            self.orchestrator.nuevo_orchestrator(orchestrator)

    def downloadTask(self, url, current=None):
        ''' downloadTask '''
        if self.orchestrator:
            return self.orchestrator.enviar_downloader(url)

    def getFileList(self, current=None):
        ''' getFileList '''
        if self.orchestrator:
            return self.orchestrator.obtener_lista_canciones()
        return []


class FileUpdatesEventI(TrawlNet.UpdateEvent):
    '''
    FileUpdatesEventI
    '''
    orchestrator = None

    def newFile(self, file_info, current=None):
        '''newFile'''
        if self.orchestrator:
            file_hash = file_info.hash
            if file_hash not in self.orchestrator.files_update:
                self.orchestrator.files_update[file_hash] = file_info.name



class IniciarOrchestrator:

    ''' Iniciar orchestrators '''

    qos = {}
    orchestrators_dict = {}
    files_update = {}

    def __init__(self, broker, downloader_proxy, topic_update, topic_orchestrator):
        ''' Constructor '''
        self.adapter = broker.createObjectAdapter("OrchestratorAdapter")
        self.crear_orchestrator(broker, downloader_proxy, topic_update, topic_orchestrator)
        self.downloader = TrawlNet.DownloaderPrx.checkedCast(broker.stringToProxy(downloader_proxy))
        self.topic_orchestrator = topic_orchestrator
        self.file_topic = topic_update
        self.crear_orchestrator_event()
        self.crear_file_update_event()
        self.lanzar()

    def crear_orchestrator(self, broker, downloader_proxy, topic_update, topic_orchestrator):
        ''' Crear orchestrator'''
        self.orchestrator = OrchestratorI()
        self.orchestrator.orchestrator = self
        self.proxy_orchestrator = self.adapter.addWithUUID(self.orchestrator)

    def crear_file_update_event(self):
        ''' Crear FileUpdatesEventI '''
        self.file_updates = FileUpdatesEventI()
        self.file_updates.orchestrator = self
        self.file_updates_proxy = self.adapter.addWithUUID(self.file_updates)
        self.file_topic.subscribeAndGetPublisher(self.qos, self.file_updates_proxy)

    def crear_orchestrator_event(self):
        ''' Sincronizar orchestrators'''
        self.subscriptor = OrchestratorEventI()
        self.subscriptor.orchestrator = self
        self.proxy_subscriptor = self.adapter.addWithUUID(self.subscriptor)
        self.topic_orchestrator.subscribeAndGetPublisher(self.qos, self.proxy_subscriptor)
        self.publisher = TrawlNet.OrchestratorEventPrx.uncheckedCast(self.topic_orchestrator.getPublisher())

    def saludar(self, orchestrator):
        ''' Decir hola a un orchestrator'''
        if orchestrator.ice_toString() in self.orchestrators_dict:
            return
        print("Hola! soy el orchestrator %s" % orchestrator.ice_toString())
        self.orchestrators_dict[orchestrator.ice_toString()] = orchestrator
        orchestrator.announce(TrawlNet.OrchestratorPrx.checkedCast(self.proxy_orchestrator))

    def enviar_downloader(self, url):
        ''' envio downloadTask '''
        return self.downloader.addDownloadTask(url)

    def nuevo_orchestrator(self, orchestrator):
        if orchestrator.ice_toString() in self.orchestrators_dict:
            return
        print("Hola! yo soy %s" % orchestrator.ice_toString())
        self.orchestrators_dict[orchestrator.ice_toString()] = orchestrator

    def lanzar(self):
        ''' Activar adaptador y lanzar hello orchestrator '''
        self.adapter.activate()
        self.publisher.hello(TrawlNet.OrchestratorPrx.checkedCast(self.proxy_orchestrator))

    def obtener_lista_canciones(self):
        ''' Obtener lista '''
        file_list = []
        for fhash in self.files_update:
            file_info_object = TrawlNet.FileInfo()
            file_info_object.hash = fhash
            file_info_object.name = self.files_update[fhash]
            file_list.append(file_info_object)
        return file_list

    def __str__(self):
        ''' to str '''
        return str(self.proxy_subscriptor)


SERVER = Server()
sys.exit(SERVER.main(sys.argv))
