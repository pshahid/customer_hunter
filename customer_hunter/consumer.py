import sys
import time
import string
import arrow
import logging
import re
from HTMLParser import HTMLParser
import twitter

parser = HTMLParser()

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

class ConsumerStrategy(object):
    """
    Abstract base implementation of a ConsumerStrategy, which has text-scrubbing
    capabilities, as well as date parsing ability. You must instantiate children
    of this strategy, such as FilterConsumer or LocationConsumer.
    """
    def __init__(self):
        pass

    def consume(self, stream):
        """
        A synchronous, BLOCKING method which is in charge of coordinating the consumption
        efforts of any given strategy. 

        This accepts a TwitterApi object from python-twitter
        and returns a dictionary representing a recently received tweet.
        """
        raise NotImplementedError("ConsumerStrategy has not implemented consume. This class hasn't been subclassed.")

    def _scrub(self, text):
        try:
            #Parse annoying HTML characters like &amp;
            text = parser.unescape(text)

            #Remove extra newlines & carriage returns and make whole thing lowercase
            text = text.replace("\n", "").replace("\r", "").lower()
            
            #Remove all punctuation except those in ignore
            ignore = ("@", "#", "/")
            for punct in string.punctuation:
                if punct not in ignore:
                    text = text.replace(punct, "")

            #Remove non-ascii chars (emoticons and shit)
            text = "".join(c if ord(c) < 128 else "" for c in text)

            #Remove excess space
            text = re.sub("(\s+)", " ", text)
        except TypeError as te:
            logging.error(te)
            logging.error(text)

        return text

    def _remove_all_tweet_urls(self, tweet):
        text = tweet["text"]

        if "entities" in tweet:
            #Strangely, URLs will always be there, but media won't
            urls = tweet["entities"]["urls"]

            for url in urls:
                text = self._remove_url(text, url["indices"][0], url["indices"][1])

            if "media" in tweet["entities"]:
                for media in tweet["entities"]["media"]:
                    text = self._remove_url(text, media["indices"][0], media["indices"][1])

        return text

    def _remove_url(self, text, lindex=-1, rindex=-1):
        '''
        Return given text with all URLs removed. Optional arguments start and length
        are the index where the URL starts and the length of the URL respectively. These help
        to more quickly remove the URL; use them when they are immediately available (Tweets).
        '''
        if lindex > -1 and rindex > -1:
            return text[0:lindex] + text[rindex:]
        else:
            raise NotImplementedError("remove_url currently requires 3 arguments, 1 given.")

class LocationConsumer(ConsumerStrategy):
    """
    A consumer strategy which also filters based on the given list of filters
    passed in through the constructor. 
    """
    def __init__(self, filters):
        super(LocationConsumer, self).__init__()

        if filters is not None:
            self.filters = [f.lower() for f in filters]
        else:
            self.filters = []
    
    def consume(self, stream):
        """Returns a dictionary representing a Tweet if the message passes the applied filter"""
        tweet = stream.next()

        if tweet == None:
            raise TypeError("Expected a JSON object from stream, got None instead.")

        if tweet.get("lang", None) == "en":
            msg = self._remove_all_tweet_urls(tweet)
            msg = self._scrub(msg)

            tweet['message'] = msg
            tweet['username'] = tweet.get('user').get('screen_name')
            tweet['twitter_id'] = tweet.get('id')

            if self._apply_filter(msg):
                logging.info(tweet.get('user').get('screen_name') + "/status/" + str(tweet.get('id')) + ": " + msg)
                return tweet

        return None

    def _apply_filter(self, sentence):
        if len(self.filters) > 0:
            return any([f in sentence for f in self.filters])
        else:
            return True

class FilterConsumer(ConsumerStrategy):
    """
    A bare-bones implementation of a consumer strategy.
    """
    def __init__(self):
        super(FilterConsumer, self).__init__()

    def consume(self, stream):
        tweet = stream.next()

        if tweet == None:
            raise TypeError("Expected a JSON object from stream, got None instead.")

        if tweet.get("lang", None) == "en":
            msg = self._remove_all_tweet_urls(tweet)
            msg = self._scrub(msg)

            logging.info(tweet.get('user').get('screen_name') + "/status/" + str(tweet.get('id')) + ": " + msg)

            tweet['message'] = msg
            tweet['username'] = tweet.get('user').get('screen_name')
            tweet['twitter_id'] = tweet.get('id')

            return tweet

        return None