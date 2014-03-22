import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.wamp1.protocol import exportPub, exportRpc, WampServerFactory, WampServerProtocol
import config

class Server(WampServerProtocol):

    @exportPub(config.wamp_topic) 
    def sendFeed(self, topicUri, event):
        print "sendFeed ", topicUri, event

    def onSessionOpen(self):
        self.registerForPubSub(config.wamp_topic)

def build_server_factory():
    factory = WampServerFactory("ws://" + config.domain)
    factory.protocol = Server
    factory.setProtocolOptions(allowHixie76 = True)

    return factory