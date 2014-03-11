import sys
import time
import string
import datetime
import logging
import re
from HTMLParser import HTMLParser
import twitter

parser = HTMLParser()

'''
Callback is the function passed whenever a new tweet is inserted into the database.
'''
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
            logging.debug("Verifying credentials.")
            self.user = self.api.VerifyCredentials()

            #Choose between a locations-based or filters-based consumer.
            #It should not appear any different outwardly
            if self.locations is None:
                self.stream = self.api.GetStreamFilter(tracks=filters)
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
    def __init__(self):
        pass

    def consume(self, stream):
        raise NotImplementedError("ConsumerStrategy has not implemented consume. This class hasn't been subclassed.")

    '''
    Return given text with HTML parsed into normal UTF-16 and remove new lines. 
    Raises a TypeError if argument text is None. Also removes punctuation.
    '''
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
            #We have to take out the timezone because python doesn't support %z in 2.7
            #Twitter's timezone will ALWAYS be +0000 for any created_at fields.
            #This is not the case for other networks though!!
            date = date.replace("+0000 ", "")

            return datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Y')
        else:
            return datetime.datetime.now()

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

    '''
    Return given text with all URLs removed. Optional arguments start and length
    are the index where the URL starts and the length of the URL respectively. These help
    to more quickly remove the URL; use them when they are immediately available (Tweets).
    '''
    def _remove_url(self, text, lindex=-1, rindex=-1):
        if lindex > -1 and rindex > -1:
            return text[0:lindex] + text[rindex:]
        else:
            raise NotImplementedError("remove_url currently requires 3 arguments, 1 given.")

class LocationConsumer(ConsumerStrategy):

    def __init__(self, filters, filter_fn=None):
        super(LocationConsumer, self).__init__()

        if filters is not None:
            self.filters = [f.lower() for f in filters]
        else:
            self.filters = []

        if filter_fn is not None:
            self.filter_fn = filter_fn
        else:
            self.filter_fn = self._apply_filter

    '''
    Returns a Tweet model if the message passes the applied filter
    '''
    def consume(self, stream):
        tweet = stream.next()

        if tweet == None:
            raise TypeError("Expected a JSON object from stream, got None instead.")

        if tweet.get("lang", None) == "en":
            date = self._parse_date(tweet.get('created_at'))

            msg = self._remove_all_tweet_urls(tweet)
            msg = self._scrub(msg)

            logging.info(tweet.get('user').get('screen_name') + "/status/" + str(tweet.get('id')) + ": " + msg)

            new_tweet = {
                'message': msg,
                'created_date': date,
                'twitter_id': tweet.get('id'), 
                'username': tweet.get('user').get('screen_name'),
                'in_reply_to_screen_name': tweet.get('in_reply_to_screen_name'),
                'in_reply_to_user_id': tweet.get('in_reply_to_user_id'),
                'in_reply_to_status_id': tweet.get('in_reply_to_status_id')
            }

            if self.filter_fn(msg):
                return new_tweet

        return None

    '''
    Returns true if any of filters is in sentence. This sentence is assumed to have been scrubbed
    already, and the filters are not case sensitive.
    '''
    def _apply_filter(self, sentence):
        if len(self.filters) > 0:
            for f in self.filters:
                if f in sentence:
                    return True
            return False
        else:
            return True

class FilterConsumer(ConsumerStrategy):
    def __init__(self):
        super(FilterConsumer, self).__init__()

    def consume(self, stream):
        tweet = stream.next()

        if tweet == None:
            raise TypeError("Expected a JSON object from stream, got None instead.")

        if tweet.get("lang", None) == "en":
            date = self._parse_date(tweet.get('created_at'))

            msg = self._remove_all_tweet_urls(tweet)
            msg = self._scrub(msg)

            logging.info(tweet.get('user').get('screen_name') + "/status/" + str(tweet.get('id')) + ": " + msg)

            new_tweet = {
                'message': msg,
                'created_date': date,
                'twitter_id': tweet.get('id'), 
                'username': tweet.get('user').get('screen_name'),
                'in_reply_to_screen_name': tweet.get('in_reply_to_screen_name'),
                'in_reply_to_user_id': tweet.get('in_reply_to_user_id'),
                'in_reply_to_status_id': tweet.get('in_reply_to_status_id')
            }

            return new_tweet

        return None