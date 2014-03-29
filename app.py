import logging
import sys
import json
from peewee import *
from models import Tweet
import config
from consumer import TwitterConsumer
from modeler import Modeler

import server 
import app
from autobahn.twisted.websocket import listenWS
from twisted.internet import defer, threads, reactor
from twisted.internet.task import LoopingCall

dbconn = MySQLDatabase(config.db, user=config.user, passwd=config.password)

def start():
    _setup_logging()
    
    Tweet.create_table(fail_silently=True)

    modeler = Modeler(config.training, config.test)
    modeler.load_training()
    modeler.load_test()

    filters = config.filters
    bounding_box = config.bounding_box
    api_kwargs = config.oauth

    app.factory = server.build_server_factory()

    listenWS(app.factory)

    app.consumer = TwitterConsumer(api_kwargs, filters=filters, bounding_box=bounding_box)
    app.consumer.start()

    def ping_broadcast():
        app.factory.dispatch(config.wamp_topic, json.dumps({"ping": ""}))
    
    lc = LoopingCall(ping_broadcast)
    lc.start(300)

def stop():
    reactor.stop()
    app.consumer.stop()

def consume():
    df = threads.deferToThread(app.consumer.consume)
    df.addCallback(_consume_callback)
    df.addErrback(_consume_errback)

def _consume_callback(tweet):
    if tweet is not None:
        #Creates the Tweet model and prepares it to be saved in the DB
        new_tweet = Tweet(\
            message=tweet['message'],\
            created_date=tweet['created_date'],\
            twitter_id=tweet['twitter_id'], \
            username=tweet['username'], \
            in_reply_to_screen_name=tweet['in_reply_to_screen_name'],\
            in_reply_to_user_id=tweet['in_reply_to_user_id'],\
            in_reply_to_status_id=tweet['in_reply_to_status_id']
        )
        tweet['created_date'] = str(tweet['created_date'])
        tweet['twitter_id'] = str(tweet['twitter_id'])

        app.factory.dispatch(config.wamp_topic, json.dumps(tweet))
        # if self.modeler is not None and tweet['message'] is not None:
            # predictions = self.modeler.predict([tweet['message']])

            # new_tweet.logit_prediction = int(predictions['logit'][0])
            # new_tweet.sgd_prediction = int(predictions['sgd'][0])
        new_tweet.save()

        
        # self.factory.protocol.updateFeed(self.factory)

    consume()

def _consume_errback(data):
    print "ERRORBACK"
    print data
    consume()

def _setup_logging():
    logging.basicConfig(level=logging.INFO, filename='consumer.log', \
        format='%(asctime)s - %(message)s ', datefmt=config.datefmt)

def get_last(date):
    dbconn.connect()
    return Tweet.select().where(Tweet.created_date <= date).order_by(Tweet.created_date.desc()).limit(10)

if __name__ == "__main__":
    try:
        reactor.callWhenRunning(app.start)
        reactor.callWhenRunning(webapp.run)
        reactor.run()
    except KeyboardInterrupt:
        stop()
        sys.exit(0)
    except:
        print(sys.exc_info()[1])
        logging.warning(sys.exc_info()[1])

        stop()
        sys.exit(0)
