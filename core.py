import logging
import sys
import json
import config
import os
from twisted.internet import defer, threads, reactor
from twisted.internet.task import LoopingCall
from twisted.python import log
from autobahn.wamp1.protocol import WampClientProtocol, WampClientFactory
from autobahn.twisted.websocket import connectWS
from peewee import *
import models
import datetime

class ClientContainer(object):
    """
    Adapter/container for the WAMP client, essentially keeps us 
    from using global variables all the time.

    """
    WAMPClient = None

    def setClient(self, c):
        self.WAMPClient = c

    def sendSocialData(self, data):
        self.WAMPClient.sendSocialData(data)

client = ClientContainer()

def setClient(c):
    client.WAMPClient = c

def start():

    def ping_broadcast():
        client.sendSocialData(json.dumps({"ping": ""}))
    
    lc = LoopingCall(ping_broadcast)
    print "Starting ping looping call"
    lc.start(300)

def stop():
    reactor.stop()

def _setup_logging():
    logging.basicConfig(level=logging.INFO, filename='consumer.log', \
        format='%(asctime)s - %(message)s ', datefmt=config.datefmt)

class Client(WampClientProtocol):
    """
    Client for the WAMP server. Every time a consumer reports back
    with data it will call sendSocialData(), which will transmit data
    over a network connection on localhost to the server, which will
    broadcast out to connected web clients.
    """
    def onSessionOpen(self):
        factory.client = self
        client.setClient(self)

        log.msg("Session opened")

        start()

    def sendSocialData(self, data):
        self.publish(config.wamp_topic, data)

if __name__ == "__main__":
    _setup_logging()

    # Listen on the WAMP server port and domain
    factory = WampClientFactory('ws://' + config.domain + ':' + str(config.port))
    factory.protocol = Client
    connectWS(factory)

    def before_shutdown():
        log.msg('Shutting down')

    def after_shutdown():
        sys.exit(0)

    reactor.addSystemEventTrigger('before', 'shutdown', before_shutdown)
    reactor.addSystemEventTrigger('after', 'shutdown', after_shutdown)
    reactor.run()
