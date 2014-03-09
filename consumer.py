import sys
import time
import string
import datetime
import logging
from HTMLParser import HTMLParser
from peewee import *
from models import * 
import twitter
import config


dbconn = MySQLDatabase(config.db, user=config.user, passwd=config.password)
parser = HTMLParser()

def main():
    setup_logging()
    dbconn.connect()
    Tweet.create_table(fail_silently=True)
    # User.create_table(fail_silently=True)

    logging.debug("Initializing the consumer...")

    api = twitter.Api(\
        consumer_key=config.api_key,\
        consumer_secret=config.api_secret,\
        access_token_key=config.access_token, 
        access_token_secret=config.access_secret)

    logging.debug("Verifying credentials.")

    user = api.VerifyCredentials()

    filters = [
        "verizon",
        "tmobile",
        "t-mobile",
        "at&t",
        "sprint"
    ]

    #Charleston area bounding box
    bounding_box = ["-80.441697, 32.512679", "-79.614146, 33.590588"]

    logging.debug("Filter set, creds verified, grabbing stream.")

    start_time = time.time()
    stream = api.GetStreamFilter(locations=bounding_box)
    total_tweets = 0

    try:
        tweet = None
        while True:
            tweet = stream.next()
            total_tweets = total_tweets + 1

            if tweet.get("lang", None) == "en":
                date = parse_date(tweet.get('created_at'))

                msg = remove_all_tweet_urls(tweet)
                msg = scrub(msg)

                logging.debug(tweet.get('user').get('screen_name') + "/status/" + str(tweet.get('id')) + ": " + msg)

                new_tweet = Tweet(
                    message=msg,
                    created_date=date,
                    twitter_id=tweet.get('id'),
                    username=tweet.get('user').get('screen_name'),
                    in_reply_to_screen_name=tweet.get('in_reply_to_screen_name'),
                    in_reply_to_user_id=tweet.get('in_reply_to_user_id'),
                    in_reply_to_status_id=tweet.get('in_reply_to_status_id')
                )

                new_tweet.save()
    except StopIteration:
        logging.critical("Stream can't move on.")
    except KeyboardInterrupt:
        logging.critical("Keyboard Interrupt detected, exiting.")
    except InternalError as e:
        logging.error(e)
        logging.error("Encountered a tweet that likely had unicode.")



    end_time = time.time()
    seconds = end_time - start_time
    minutes = (end_time - start_time) / 60.0
    logging.info("Total tweets: ", total_tweets)
    logging.info("Seconds running: ", seconds)
    logging.info("Minutes running: ", minutes)
    logging.info("Tweets per minute: %d" % float(total_tweets / minutes))

    sys.exit(0)

def setup_logging():
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARNING,
        'ERROR': logging.ERROR
        'CRIT': logging.CRITICAL
    }

    level = levels[config.level]

    logging.basicConfig(filename=config.filename, level=level, format=config.format, datefmt=config.datefmt)

'''
Return given text with HTML parsed into normal UTF-16 and remove new lines. 
Raises a TypeError if argument text is None. Also removes punctuation.
'''
def scrub(text):
    #Parse annoying HTML characters like &amp;
    try:
        text = parser.unescape(text)

        #Get rid of extra newlines & carriage returns and make whole thing lowercase
        text = text.replace("\n", "").replace("\r", "").lower()
        
        #Get rid of punctuation
        text = text.translate(string.punctuation)
    except TypeError as te:
        print te
        print text

    return text

'''
Return given text with all URLs removed. Optional arguments start and length
are the index where the URL starts and the length of the URL respectively. These help
to more quickly remove the URL; use them when they are immediately available (Tweets).
'''
def remove_url(text, lindex=-1, rindex=-1):
    if lindex > -1 and rindex > -1:
        return text[0:lindex] + text[rindex:]
    else:
        raise NotImplementedError("remove_url currently requires 3 arguments, 1 given.")

def remove_all_tweet_urls(tweet):
    text = tweet["text"]

    if "entities" in tweet:
        #Strangely, URLs will always be there, but media won't
        urls = tweet["entities"]["urls"]

        for url in urls:
            text = remove_url(text, url["indices"][0], url["indices"][1])

        if "media" in tweet["entities"]:
            for media in tweet["entities"]["media"]:
                text = remove_url(text, media["indices"][0], media["indices"][1])

    return text


def parse_date(date):
    if date != None:
        #We have to take out the timezone because python doesn't support %z in 2.7
        #Twitter's timezone will ALWAYS be +0000 for any created_at fields.
        #This is not the case for other networks though!!
        date = date.replace("+0000 ", "")

        return datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Y')
    else:
        return datetime.datetime.now()

if __name__ == "__main__":
    main()