import logging
import sys
from peewee import *
from models import * 
import config
from consumer import TwitterConsumer

dbconn = MySQLDatabase(config.db, user=config.user, passwd=config.password)

class App(object):
    def __init__(self):
        self.consumer = None

    def start(self):
        self._setup_logging()
        dbconn.connect()
        Tweet.create_table(fail_silently=True)
        # User.create_table(fail_silently=True)
        # Prediction.create_table(fail_silently=True)

        filters = [
            "verizon",
            "tmobile",
            "t-mobile",
            "at&t",
            "sprint"
        ]

        bounding_box = ["-80.441697, 32.512679", "-79.614146, 33.590588"]

        api_kwargs = {
            'api_key': config.api_key,
            'api_secret': config.api_secret,
            'access_key': config.access_token,
            'access_secret': config.access_secret
        }
        self.consumer = TwitterConsumer(api_kwargs, bounding_box=bounding_box)
        self.consumer.start()

        while True:
            tweet = self.consumer.consume()
            if tweet is not None:
                #Creates and saves the tweet in the DB
                new_tweet = Tweet(\
                    message=tweet['message'],\
                    created_date=tweet['created_date'],\
                    twitter_id=tweet['twitter_id'], \
                    username=tweet['username'], \
                    in_reply_to_screen_name=tweet['in_reply_to_screen_name'],\
                    in_reply_to_user_id=tweet['in_reply_to_user_id'],\
                    in_reply_to_status_id=tweet['in_reply_to_status_id']
                )

                new_tweet.save()


    def stop(self):
        self.consumer.stop()

    def _setup_logging(self):
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRIT': logging.CRITICAL
        }

        level = levels[config.level]
        logging.basicConfig(filename=config.filename, level=level, format=config.format, datefmt=config.datefmt)

if __name__ == "__main__":
    app = None
    try:
        app = App()
        app.start()
    except KeyboardInterrupt:
        if app:
            app.stop()
        sys.exit(0)