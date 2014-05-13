import logging
import sys
import json
import config
import os
from twisted.internet import defer, threads, reactor
from twisted.internet.task import LoopingCall
from autobahn.twisted.websocket import listenWS
from autobahn.wamp1.protocol import exportPub, exportRpc, WampServerFactory, WampServerProtocol
from twisted.python import log
from peewee import *
import models
import modeler
import consumer
import datetime

modeler_inst = modeler.Modeler(config.training, config.test)

filters = config.filters
bounding_box = config.bounding_box
api_kwargs = config.oauth
consumer = consumer.TwitterConsumer(api_kwargs, filters=filters, bounding_box=bounding_box)

db = MySQLDatabase("social_consumer", user=config.user, passwd=config.password)

def init_db():
    db.connect()
    models.Tweet.create_table(fail_silently=True)

def start():    
    consumer.start()
    consume()
    def ping_broadcast():
        factory.dispatch(config.wamp_topic, json.dumps({"ping": ""}))
    
    lc = LoopingCall(ping_broadcast)
    lc.start(300)

def stop():
    reactor.stop()
    consumer.stop()

def consume():
    df = threads.deferToThread(consumer.consume)
    df.addCallback(_consume_callback)
    df.addErrback(_consume_errback)

def _consume_callback(tweet):
    if tweet is not None:
        db.connect()
        #Creates the Tweet model and prepares it to be saved in the DB
        new_tweet = models.Tweet(\
            message=tweet['message'],\
            created_date=tweet['created_date'],\
            twitter_id=tweet['twitter_id'], \
            username=tweet['username'], \
            in_reply_to_screen_name=tweet['in_reply_to_screen_name'],\
            in_reply_to_user_id=tweet['in_reply_to_user_id'],\
            in_reply_to_status_id=tweet['in_reply_to_status_id'],
            prediction_label=-1
        )
        tweet['created_date'] = str(tweet['created_date'])
        tweet['twitter_id'] = str(tweet['twitter_id'])

        if tweet['coordinates'] is not None and 'point' in tweet['coordinates']:
            new_tweet.longitude = tweet['coordinates']['coordinates'][0]
            new_tweet.latitude = tweet['coordinates']['coordinates'][1]

        if modeler_inst is not None and tweet['message'] is not None:
            predictions = modeler_inst.predict([tweet['message']])

            new_tweet.logit_prediction = int(predictions['logit'][0])
            new_tweet.sgd_prediction = int(predictions['sgd'][0])

        if int(predictions['logit'][0]) == 1 and int(predictions['sgd'][0]) == 1:
            factory.dispatch(config.wamp_topic, json.dumps(tweet))
        
        new_tweet.save()

    consume()

def _consume_errback(data):
    print "ERRORBACK"
    log.msg('Errback triggered: ' + str(data))
    consume()

def _setup_logging():
    logging.basicConfig(level=logging.INFO, filename='consumer.log', \
        format='%(asctime)s - %(message)s ', datefmt=config.datefmt)

def get_last(date):
    db.connect()
    # return models.Tweet.select()
    return models.Tweet.select().where( \
        (models.Tweet.created_date <= date) & \
        ((models.Tweet.prediction_label == 1) | \
        ((models.Tweet.sgd_prediction == 1) & models.Tweet.logit_prediction == 1))).order_by(models.Tweet.created_date.desc()).limit(10)

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
            log.msg(sys.exc_info()[1])
        else:
            return tweets

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
        self.registerMethodForRpc('#acceptable', self, Server.register_acceptable)
        self.registerMethodForRpc('#unacceptable', self, Server.register_unacceptable)

log.startLogging(open('./twisted-output.log', 'w'))
factory = WampServerFactory("ws://" + config.domain + "/wamp")
factory.protocol = Server
factory.setProtocolOptions(allowHixie76 = True)

if __name__ == "__main__":
    _setup_logging()
    init_db()

    modeler_inst.load_training()
    modeler_inst.load_test()

    reactor.callWhenRunning(start)
    def before_shutdown():
        log.msg('Shutting down')
    reactor.addSystemEventTrigger('before', 'shutdown', before_shutdown)
    listenWS(factory)
    reactor.run()
    # try:
    #     reactor.run()
    # except KeyboardInterrupt:
    #     stop()
    #     sys.exit(0)
    # except:
    #     print(sys.exc_info()[1])
    #     logging.warning(sys.exc_info()[1])

    #     stop()
    #     sys.exit(0)
