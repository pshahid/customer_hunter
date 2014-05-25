from twisted.internet import reactor
from autobahn.twisted.websocket import listenWS
from autobahn.wamp1.protocol import exportPub, exportRpc, WampServerFactory, WampServerProtocol
from twisted.python import log
from peewee import *
from pymongo import MongoClient
import config
import models
import sys
import datetime
from bson.json_util import dumps

db = MySQLDatabase("social_consumer", threadlocals=True, user=config.user, passwd=config.password)
mongo_db = MongoClient()

class Server(WampServerProtocol):

    def getInit(self, date):
        try:
            if date is None or date == '':
                parsed_date = datetime.datetime.now()
            else:
                parsed_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')

            obj = get_last(parsed_date)
            tweets = [str(tweet) for tweet in obj]
        except ValueError:
            log.msg(sys.exc_info()[1])
            return 'Error: That date was not parseable.'
        except:
            log.msg('Error in get init')
            log.msg(sys.exc_info()[0])
            log.msg(sys.exc_info()[1])
        else:
            return tweets

    def getInitMongo(self):
        json_string = ''

        try:
            json_string = dumps(get_last_mongo())
        except:
            log.msg('Tried to do the thing')
            log.msg(sys.exc_info()[0])
            log.msg(sys.exc_info()[1])
        else:
            return json_string

    def register_acceptable(self, tweet_id):
        try:
            tid = int(tweet_id)
            t = models.Tweet.get(models.Tweet.twitter_id == tid)
        except DoesNotExist:
            log.msg("Attempting to train from a tweet that doesn't exist. TID: " + str(tid))
        except AttributeError:
            log.msg('AttributeError: ' + str(sys.exc_info()[0]))
        else:
            t.prediction_label = 1
            t.save()

    def register_unacceptable(self, tweet_id):
        try:
            tid = int(tweet_id)
            t = models.Tweet.get(models.Tweet.twitter_id == tid)
        except DoesNotExist:
            log.msg("Attempting to train from a tweet that doesn't exist. TID: " + str(tid))
        except AttributeError:
            log.msg('AttributeError: ' + str(sys.exc_info()[0]))
        else:
            t.prediction_label = 0
            t.save()

    def onSessionOpen(self):
        self.registerForPubSub(config.wamp_topic)
        self.registerMethodForRpc("#getInit", self, Server.getInit)
        self.registerMethodForRpc('#getInitMongo', self, Server.getInitMongo)
        self.registerMethodForRpc('#acceptable', self, Server.register_acceptable)
        self.registerMethodForRpc('#unacceptable', self, Server.register_unacceptable)

def get_last(date):
    db.connect()
    # return models.Tweet.select()
    return models.Tweet.select().where( \
        (models.Tweet.created_date <= date) & \
        ((models.Tweet.prediction_label == 1) | \
        ((models.Tweet.sgd_prediction == 1) & models.Tweet.logit_prediction == 1))).order_by(models.Tweet.created_date.desc()).limit(10)

def get_last_mongo():
    return [m for m in mongo_db.social_consumer.tweets.find(limit=20)]

def init_db():
    db.connect()
    models.Tweet.create_table(fail_silently=True)

if __name__ == '__main__':
    init_db()
    log.startLogging(open('./twisted-output.log', 'w'))
    factory = WampServerFactory("ws://" + config.domain + ":9001/wamp")
    factory.protocol = Server
    factory.setProtocolOptions(allowHixie76 = True)
    listenWS(factory)

    reactor.run()