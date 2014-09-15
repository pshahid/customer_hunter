import sys
import time
import string
import arrow
import logging
import re
from HTMLParser import HTMLParser

parser = HTMLParser()

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

    def _parse_date(self, date):

        if date != None:
            fmt = 'ddd MMM D HH:mm:ss Z YYYY'
            return arrow.get(date, fmt).datetime
        else:
            return arrow.utcnow().datetime

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
        try:
            tweet = stream.next()
        except StopIteration:
            print "Stream stopped from twitter for whatever reason"

        if tweet == None:
            raise TypeError("Expected a JSON object from stream, got None instead.")

        if tweet.get("lang", None) == "en":
            msg = self._remove_all_tweet_urls(tweet)
            msg = self._scrub(msg)
            date = self._parse_date(tweet.get('created_at', None))

            tweet['message'] = msg
            tweet['username'] = tweet.get('user').get('screen_name')
            tweet['twitter_id'] = tweet.get('id')
            tweet['created_date'] = date
            
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
        try:
            tweet = stream.next()
        except StopIteration:
            print "Stream stopped from twitter for whatever reason"

        if tweet == None:
            raise TypeError("Expected a JSON object from stream, got None instead.")

        if tweet.get("lang", None) == "en":
            msg = self._remove_all_tweet_urls(tweet)
            msg = self._scrub(msg)
            date = self._parse_date(tweet.get('created_at'))

            logging.info(tweet.get('user').get('screen_name') + "/status/" + str(tweet.get('id')) + ": " + msg)

            tweet['message'] = msg
            tweet['username'] = tweet.get('user').get('screen_name')
            tweet['twitter_id'] = tweet.get('id')
            tweet['created_date'] = date

            return tweet

        return None