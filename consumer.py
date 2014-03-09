import sys
import time
import string
from datetime import datetime
from HTMLParser import HTMLParser
from peewee import *
from models import * 
import twitter
import config


dbconn = MySQLDatabase(config.db, user=config.user, passwd=config.password)
parser = HTMLParser()

def main():
    dbconn.connect()
    Tweet.create_table(fail_silently=True)
    # User.create_table(fail_silently=True)

    print("Initializing the consumer...")
    api = twitter.Api(\
        consumer_key=config.api_key,\
        consumer_secret=config.api_secret,\
        access_token_key=config.access_token, 
        access_token_secret=config.access_secret)

    print("Verifying credentials.")
    user = api.VerifyCredentials()

    filters = [
        "verizon",
        "tmobile",
        "t-mobile",
        "at&t",
        "sprint"
    ]

    # bounding_box = ["-80.93,32.06", "-79.46,33.24"]
    # bounding_box = ["-122.66,37.45","-122.03,38.01"]
    bounding_box = ["-80.441697, 32.512679", "-79.614146, 33.590588"]
    print("Filter set, creds verified, grabbing stream.")

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

                msg = remove_all_tweet_urls(tweet.get('text'))
                msg = scrub(msg)

                new_tweet = Tweet(
                    message=msg,
                    created_date=date,
                    twitter_id=tweet.get('id'),
                    user=tweet.get('user').get('screen_name'),
                    in_reply_to_screen_name=tweet.get('in_reply_to_screen_name'),
                    in_reply_to_user_id=tweet.get('in_reply_to_user_id'),
                    in_reply_to_status_id=tweet.get('in_reply_to_status_id')
                )

                new_tweet.save()
    except StopIteration:
        print("Stream can't move on.")
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected, exiting")
    except InternalError:
        print("Encountered a tweet that likely had unicode.")



    end_time = time.time()
    seconds = end_time - start_time
    minutes = (end_time - start_time) / 60.0
    print "Total tweets: ", total_tweets
    print "Seconds running: ", seconds
    print "Minutes running: ", minutes
    print "Tweets per minute: %d" % float(total_tweets / minutes)

    sys.exit(0)

'''
Return given text with HTML parsed into normal UTF-16 and remove new lines. 
Raises a TypeError if argument text is None. Also removes punctuation.
'''
def scrub(text):
    #Parse annoying HTML characters like &amp;
    text = parser.unescape(text)

    #Get rid of extra newlines & carriage returns and make whole thing lowercase
    text = text.replace("\n", "").replace("\r", "").lower()
    
    #Get rid of punctuation
    text = text.translate(string.maketrans("",""), string.punctuation)

    return text

'''
Return given text with all URLs removed. Optional arguments start and length
are the index where the URL starts and the length of the URL respectively. These help
to more quickly remove the URL; use them when they are immediately available (Tweets).
'''
def remove_url(text, start=-1, length=-1):
    if start > -1 and length > -1:
        return text[0:start] + text[1 + start + length:]

def remove_all_tweet_urls(tweet):
    if "entities" in tweet:
        text = tweet["text"]
        urls = tweet["entities"]["urls"]

        for url in urls:
            text = remove_url(url["url"])

    return text


def parse_date(date):
    if date != None:
        #We have to take out the timezone because python doesn't support %z in 2.7
        #Twitter's timezone will ALWAYS be +0000 for any created_at fields.
        #This is not the case for other networks though!!
        date = date.replace("+0000 ", "")

        return datetime.strptime(date, '%a %b %d %H:%M:%S %Y')
    else:
        return datetime.now()

if __name__ == "__main__":
    main()