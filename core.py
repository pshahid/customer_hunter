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
from pymongo import MongoClient
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

mongo_db = MongoClient()

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

def init_db():
    db.connect()
    models.Tweet.create_table(fail_silently=True)

def start():    
    consumer.start()
    consume()

    def ping_broadcast():
        client.sendSocialData(json.dumps({"ping": ""}))
    
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

            tweet['logit_prediction'] = int(predictions['logit'][0])
            tweet['sgd_prediction'] = int(predictions['sgd'][0])

        if int(predictions['logit'][0]) == 1 and int(predictions['sgd'][0]) == 1:
            client.sendSocialData(json.dumps(tweet))
        
        new_tweet.save()

        mongo_db.social_consumer.tweets.insert(tweet)

    consume()

def _consume_errback(data):
    log.msg('Errback triggered: ' + str(data))
    consume()

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
        start()

    def sendSocialData(self, data):
        self.publish(config.wamp_topic, data)

if __name__ == "__main__":
    _setup_logging()
    init_db()

    modeler_inst.load_training()
    modeler_inst.load_test()

    # Listen on the WAMP server port and domain
    factory = WampClientFactory('ws://' + config.domain)
    factory.protocol = Client
    connectWS(factory)

    def before_shutdown():
        log.msg('Shutting down')

    def after_shutdown():
        sys.exit(0)

    reactor.addSystemEventTrigger('before', 'shutdown', before_shutdown)
    reactor.addSystemEventTrigger('after', 'shutdown', after_shutdown)
    
    reactor.run()
