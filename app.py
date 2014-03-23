import logging
import sys
import json
from peewee import *
from models import Tweet
import config
from consumer import TwitterConsumer
from modeler import Modeler

import server 
from autobahn.twisted.websocket import listenWS
from twisted.internet import defer, threads, reactor
from twisted.internet.task import LoopingCall

dbconn = MySQLDatabase(config.db, user=config.user, passwd=config.password)

class AppRef(object):
    pass

app_ref = AppRef()
app_ref.app = None

class App(object):
    def __init__(self):
        self.consumer = None
        self.factory = None
        self.modeler = None    

    def meta_start(self):

        def ping_broadcast():
            self.factory.dispatch(config.wamp_topic, json.dumps({"ping": ""}))

        lc = LoopingCall(ping_broadcast)
        lc.start(300)

        reactor.callInThread(self.start)

    def start(self):
        self._setup_logging()
        dbconn.connect()
        
        Tweet.create_table(fail_silently=True)
        # User.create_table(fail_silently=True)
        # Prediction.create_table(fail_silently=True)
        
        self.modeler = Modeler(config.training, config.test)
        self.modeler.load_training()
        self.modeler.load_test()

        filters = config.filters
        bounding_box = config.bounding_box
        api_kwargs = config.oauth

        self.consumer = TwitterConsumer(api_kwargs, \
            filters=filters, \
            bounding_box=bounding_box)

        self.consumer.start()

        self._consume()


    def _consume(self):
        df = threads.deferToThread(self.consumer.consume)
        df.addCallback(self._consume_callback)
        df.addErrback(self._consume_errback)

    def _consume_callback(self, tweet):
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

            self.factory.dispatch(config.wamp_topic, json.dumps(tweet))
            # if self.modeler is not None and tweet['message'] is not None:
                # predictions = self.modeler.predict([tweet['message']])

                # new_tweet.logit_prediction = int(predictions['logit'][0])
                # new_tweet.sgd_prediction = int(predictions['sgd'][0])
            new_tweet.save()

            
            # self.factory.protocol.updateFeed(self.factory)

        self._consume()

    def _consume_errback(self, data):
        print "ERRORBACK"
        print data
        self._consume()

    def stop(self):
        self.consumer.stop()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, filename='consumer.log', \
            format='%(asctime)s - %(message)s ', datefmt=config.datefmt)

def get_last():
    dbconn.connect()
    return Tweet.select().order_by(Tweet.created_date.desc()).limit(10)
            # return "I like biscuits and taters"

if __name__ == "__main__":
    try:
        app = App()
        app.factory = server.build_server_factory()
        listenWS(app.factory)
        reactor.callWhenRunning(app.meta_start)
        reactor.run()

    except KeyboardInterrupt:
        if app:
            app.stop()

        sys.exit(0)
    except:
        print(sys.exc_info()[1])
        logging.warning(sys.exc_info()[1])
        
        app.stop()
        reactor.stop()
        sys.exit(0)
