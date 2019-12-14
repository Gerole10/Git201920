#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
 Ochestrator class Implementation
'''

import sys
import Ice # pylint: disable=E0401,E0401
import IceStorm
Ice.loadSlice('trawlnet.ice')
import TrawlNet # pylint: disable=E0401,C0413

class Orchestrator:
    def __init__(self):
        print("")

class Server(Ice.Application):  #pylint: disable=R0903
    '''
    Server
    '''
    def run(self, argv):
        '''
        Iniciando el server de ICE
        '''
        topic_mgr = self.get_topic_manager()
        topic_name = "UpdateEvents"
        topic_orchestrator = "OrchestratorSync"
        qos = {}
        qos_evt = {}

        if not topic_mgr:
            print("Invalid topic mgr")
            return 2

        broker = self.communicator()
        proxy = broker.stringToProxy(argv[1])
        download_object = TrawlNet.DownloaderPrx.checkedCast(proxy)

        if not download_object:
            raise RuntimeError('Invalid proxy instance')

        evento_actualizar_ficheros = UpdateEventI()
        files = evento_actualizar_ficheros.files

        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        evento_ficheros = adapter.addWithUUID(evento_actualizar_ficheros)

        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, evento_ficheros)

        orchestrator_event = OrchestratorEventI()
        evt_orchestrators = adapter.addWithUUID(orchestrator_event)

        try:
            topic_orch = topic_mgr.retrieve(topic_orchestrator)
        except IceStorm.NoSuchTopic:
            topic_orch = topic_mgr.create(topic_orchestrator)

        topic_orch.subscribeAndGetPublisher(qos_evt, evt_orchestrators)
        orch_servant = OrchestratorI(files)
        proxy_orch_instance = adapter.add(orch_servant, broker.stringToIdentity("orchest"))

        orch_servant.setProxy(proxy_orch_instance)
        orch_servant.setTopicandDownloader(download_object, topic_orch)
        print(proxy_orch_instance)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

    def get_topic_manager(self):
        KEY = "IceStorm.TopicManager.Proxy"
        proxy = self.communicator().propertyToProxy(KEY)
        if proxy is None:
            return None
        return IceStorm.TopicManagerPrx.checkedCast(proxy)


class OrchestratorEventI(TrawlNet.OrchestratorEvent):
    ''' Orchestrator Event I'''
    def hello(self, orchestrator, current=None):
        ''' Hello Orchestrator '''
        orchestrator.announce(orchestrator)

class OrchestratorI(TrawlNet.Orchestrator): #pylint: disable=R0903
    '''
    Orchestrator Module
    '''
    files_sync = {}

    def __init__(self, files_update):
        '''
        Constructor
        '''
        self.files_sync = files_update

    def setTopicandDownloader(self, dwn, topic_orc):
        '''
        Set topic and downloader
        '''
        orchestrators = topic_orc.getPublisher()
        self.downloader = dwn
        orchestrator = TrawlNet.OrchestratorEventPrx.uncheckedCast(orchestrators)
        orchestrator.hello(TrawlNet.OrchestratorPrx.checkedCast(self.proxy))

    def setProxy(self, prx):
        ''' Seteando el proxy '''
        self.proxy = prx

    def downloadTask(self, url, current=None): # pylint: disable=C0103, W0613
        '''
        Function download task
        '''
        print(url)
        return self.downloader.addDownloadTask(url)

    def getFileList(self, current=None):
        '''
        Get File list
        '''
        songs = []
        for fileHash in self.files_sync:
            fileInfo = TrawlNet.FileInfo()
            fileInfo.hash = fileHash
            fileInfo.name = self.files[fileHash]
            songs.append(fileInfo)
        return songs

    def announce(self, orchestrator, current=None):
        ''' Anunciando a unorchestrator '''
        print("New Orchestrator ",orchestrator)

class UpdateEventI(TrawlNet.UpdateEvent):
    ''' Update Event '''
    files = {}

    def newFile(self, fileInfo, current=None):
        ''' new File '''
        fileHash = fileInfo.hash
        if fileHash not in self.files:
            print(fileInfo.name)
            print(fileInfo.hash)
            self.files[fileHash] = fileInfo.name


ORCHESTRATOR = Server()
sys.exit(ORCHESTRATOR.main(sys.argv))
