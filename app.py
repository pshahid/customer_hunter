import logging
import sys
import json
from peewee import *
from models import * 
import config
from consumer import TwitterConsumer
from modeler import Modeler

import server 
from autobahn.twisted.websocket import listenWS
from twisted.internet import defer, threads, reactor

dbconn = MySQLDatabase(config.db, user=config.user, passwd=config.password)

class App(object):
    def __init__(self, factory, modeler=None):
        self.consumer = None
        self.factory = factory

        if modeler is not None:
            self.modeler = modeler
        else:
            self.modeler = None

    def meta_start(self):
        reactor.callInThread(self.start)

    def start(self):
        self._setup_logging()
        dbconn.connect()
        Tweet.create_table(fail_silently=True)
        # User.create_table(fail_silently=True)
        # Prediction.create_table(fail_silently=True)

        filters = config.filters
        bounding_box = config.bounding_box
        api_kwargs = config.oauth

        self.consumer = TwitterConsumer(api_kwargs, \
            filters=filters, \
            bounding_box=bounding_box)

        self.consumer.start()
        # while True:
        #     tweet = self.consumer.consume()

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
            self.factory.dispatch("http://localhost/feed", json.dumps(tweet))
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
        # levels = {
        #     'DEBUG': logging.DEBUG,
        #     'INFO': logging.INFO,
        #     'WARN': logging.WARNING,
        #     'ERROR': logging.ERROR,
        #     'CRIT': logging.CRITICAL
        # }

        # level = levels[config.level]
        logging.basicConfig(level=logging.INFO, filename='consumer.log', \
            format='%(asctime)s - %(message)s ', datefmt=config.datefmt)

if __name__ == "__main__":
    app = None
    try:
        factory = server.build_server_factory()

        modeler = Modeler(config.training, config.test)
        modeler.load_training()
        modeler.load_test()

        app = App(factory, modeler=modeler)

        listenWS(factory)

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
