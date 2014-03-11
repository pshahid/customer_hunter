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
            tweet = self.consumer.consume()  #This is where we'd send tweets off to be predicted!
            # if tweet is not None:
                # Do things
                # print tweet
            # new_tweet = Tweet(**tweet)
            # new_tweet.save()
            # print new_tweet.id

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