#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Downloader.py
'''

import sys
import hashlib
import os.path
import Ice # pylint: disable=E0401
import IceStorm
Ice.loadSlice('trawlnet.ice')
import TrawlNet # pylint: disable=E0401,C0413

from download import download_mp3

class Server(Ice.Application): # pylint: disable=R0903
    '''
    Server
    '''
    def run(self, argv): # pylint: disable=W0613,W0221
        '''
        Run
        '''
        broker = self.communicator()
        adapter = broker.createObjectAdapter("DownloaderAdapter")
        key = 'IceStorm.TopicManager.Proxy'
        topic_name = "UpdateEvents"
        proxy = self.communicator().propertyToProxy(key)
        
        if proxy is None:
            return None

        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(proxy) # pylint: disable=E1101
        if not topic_mgr:
            return 2

        try:
            topic_file = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic: # pylint: disable=E1101
            topic_file = topic_mgr.create(topic_name)


        downloader = DownloaderI()
        downloader.publisher = TrawlNet.UpdateEventPrx.uncheckedCast(topic_file.getPublisher())
        proxy = adapter.addWithUUID(downloader)

        print(proxy, flush=True)
        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

def md5_hash(filename):
    '''
    md5 checksum
    '''
    file_hash = hashlib.md5()
    with open(filename, "rb") as new_file:
        for chunk in iter(lambda: new_file.read(4096), b''):
            file_hash.update(chunk)
    return file_hash.hexdigest()


class DownloaderI(TrawlNet.Downloader):  # pylint: disable=R0903
    '''
    DownloaderI
    '''
    publisher = None

    def addDownloadTask(self, url, current=None): # pylint: disable=C0103, R0201, W0613
        '''
        addDownloadTask
        '''
        descarga = download_mp3(url)
        if not descarga:
            raise TrawlNet.DownloadError("Error")

        file_info = TrawlNet.FileInfo()
        file_info.name = os.path.basename(descarga)
        file_info.hash = md5_hash(file_info.name)

        if self.publisher:
            self.publisher.newFile(file_info)
            
        return file_info


SERVER = Server()
sys.exit(SERVER.main(sys.argv))
