import sys

from twisted.python import log

from autobahn.wamp1.protocol import exportPub, exportRpc, WampServerFactory, WampServerProtocol
from models import *
import config
import app
import json
import datetime

class Server(WampServerProtocol):

    @exportPub(config.wamp_topic) 
    def sendFeed(self, topicUri, event):
        print "sendFeed ", topicUri, event

    def getInit(self, date):
        try:
            if date is None or date == '':
                parsed_date = datetime.datetime.now()
            else:
                parsed_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')

            obj = app.get_last(parsed_date)

            tweets = [str(tweet) for tweet in obj]
        except ValueError:
            log.msg(sys.exc_info()[1])
            return 'Error: That date was not parseable.'
        except:
            log.msg(sys.exc_info()[1])
        else:
            return tweets

    def onSessionOpen(self):
        self.registerForPubSub(config.wamp_topic)
        self.registerMethodForRpc("#getInit", self, Server.getInit)

def build_server_factory():
    log.startLogging(sys.stdout)
    factory = WampServerFactory("ws://" + config.domain + "/wamp", externalPort=config.port)
    factory.protocol = Server
    factory.setProtocolOptions(allowHixie76 = True)

    return factory