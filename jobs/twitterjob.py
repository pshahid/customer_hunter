import sys

print sys.path
from consumer import LocationConsumer, FilterConsumer
import twitter
import logging
import time
from pymongo import MongoClient

class TwitterConsumer(object):
    def __init__(self, api_kwargs, filters=None, bounding_box=None):
        self.api_kwargs = api_kwargs    #Must be a dict of api kwargs
        self.started = False
        self.user = None
        self.filters = filters
        self.locations = bounding_box

        self.api = twitter.Api(\
            consumer_key=api_kwargs['api_key'],\
            consumer_secret=api_kwargs['api_secret'],\
            access_token_key=api_kwargs['access_key'],\
            access_token_secret=api_kwargs['access_secret'])

        
        self.stream = None
        self.consumer_context = None
        self.tweet_count = 0

    def start(self):
        logging.info("Starting TwitterConsumer.")

        if self.started is False:
            self.started = True

            self.start_time = time.time()
            self.tweet_count = 0

            self.user = self.api.VerifyCredentials()
            #Choose between a locations-based or filters-based consumer.
            #It should not appear any different outwardly
            if self.locations is None:
                self.stream = self.api.GetStreamFilter(track=self.filters)
                self.consumer_context = FilterConsumer()
            else:
                self.stream = self.api.GetStreamFilter(locations=self.locations)
                self.consumer_context = LocationConsumer(self.filters)

            logging.info("TwitterConsumer has started ingesting data stream.")

        else:
            logging.info("TwitterConsumer already started.")

    def stop(self):
        self.started = False
        self.stream = None
        self.user = None
        self.api = None
        self.end_time = time.time()
        seconds = self.end_time - self.start_time
        minutes = (self.end_time - self.start_time) / 60.0

        logging.info("Total tweets: %d"  % self.tweet_count)
        logging.info("Minutes running: %d" % minutes)
        logging.info("Tweets per minute: %d" % float(self.tweet_count / minutes))

        logging.info("TwitterConsumer has stopped.")

    def restart(self):
        self.stop()
        self.start()

    def consume(self):
        self.tweet_count += 1
        return self.consumer_context.consume(self.stream)

def start(prod):
    if prod is True:
        from config.customer_hunter import *
    else:
        from config.customer_hunter_dev import *

    predictor = None

    if use_modeler:
        predictor = modeler.Modeler(training, test)

        print "Building prediction service."
        predictor.load_training()

        print("Loaded training dataset from %s." % training) 
        predictor.load_test()

        print("Loaded test dataset from %s." % test)

    mongo = MongoClient()

    twitter_consumer = TwitterConsumer(oauth, filters=filters, bounding_box=bounding_box)
    print "Created Twitter Consumer"

    twitter_consumer.start()
    print "Started Twitter Ingestion"

    while True:
        tweet = twitter_consumer.consume()
        print "Got a tweet"
        if tweet is not None:
            if use_modeler:
                predictions = predictor.predict(tweet['message'])

                tweet['logit_prediction'] = int(predictions['logit'][0])
                tweet['sgd_prediction'] = int(predictions['sgd'][0])

                if tweet['logit_prediction'] == 1 and tweet['sgd_prediction'] == 1:
                    pass
            else:
                tweet['logit_prediction'] = -1
                tweet['sgd_prediction'] = -1

            print "Inserted a tweet!"
            print tweet
            # Use the mongo_collection config value here to do the db lookup
            print mongo[mongo_collection].tweets.insert(tweet)


if __name__ == '__main__':
    start()