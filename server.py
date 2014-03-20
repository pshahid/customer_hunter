import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.wamp1.protocol import exportPub, exportRpc, WampServerFactory, WampServerProtocol

class Server(WampServerProtocol):

    @exportPub("http://localhost/feed") 
    def sendFeed(self, topicUri, event):
        print "sendFeed ", topicUri, event

    def onSessionOpen(self):
        self.registerForPubSub("http://localhost/feed")

def build_server_factory():
    factory = WampServerFactory("ws://localhost:9000", debugWamp=True)
    factory.protocol = Server
    factory.setProtocolOptions(allowHixie76 = True)

    return factory