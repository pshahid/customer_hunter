import sys

print sys.path
from config.customer_hunter_dev import *
import consumer

from pymongo import MongoClient

def start():
    predictor = None

    if use_modeler:
        predictor = modeler.Modeler(training, test)

        print "Building prediction service."
        predictor.load_training()

        print("Loaded training dataset from %s." % training) 
        predictor.load_test()

        print("Loaded test dataset from %s." % test)

    mongo = MongoClient()

    twitter_consumer = consumer.TwitterConsumer(oauth, filters=filters, bounding_box=bounding_box)
    print "Created Twitter Consumer"

    twitter_consumer.start()
    print "Started Twitter Ingestion"

    while True:
        tweet = twitter_consumer.consume()
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
            mongo[mongo_collection].tweets.insert(tweet)


if __name__ == '__main__':
    start()