import sys

from twisted.python import log

from autobahn.wamp1.protocol import exportPub, exportRpc, WampServerFactory, WampServerProtocol
from models import *
import config
import app
import json

class Server(WampServerProtocol):

    @exportPub(config.wamp_topic) 
    def sendFeed(self, topicUri, event):
        print "sendFeed ", topicUri, event

    def getInit(self):
        try:
            obj = app.get_last()
            tweets = [str(tweet) for tweet in obj]
        except:
            log.msg(sys.exc_info()[1])
        else:
            return tweets

    def onSessionOpen(self):
        self.registerForPubSub(config.wamp_topic)
        self.registerMethodForRpc("ws://" + config.domain + "#getInit", self, Server.getInit)

def build_server_factory():
    log.startLogging(sys.stdout)
    factory = WampServerFactory("ws://" + config.domain)
    factory.protocol = Server
    factory.setProtocolOptions(allowHixie76 = True)

    return factory