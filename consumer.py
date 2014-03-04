import twitter
import sys
import time
import datetime
from peewee import *
from models import * 

dbconn = MySQLDatabase("social_consumer", user="root")

def main():
    dbconn.connect()

    Tweet.create_table(fail_silently=True)
    # User.create_table(fail_silently=True)

    print("Initializing the consumer...")
    api = twitter.Api(\
        consumer_key="s2amklHxL5CPIuJODNDo6g",\
        consumer_secret="vS74EYL9PsXTG3wWOlpoEREQmhcS9gKpIjJLWwHg",\
        access_token_key="125708842-bvfTWAHUwGqrd3LE5wDHCeuOxpHlGki7H4G4oEKb", 
        access_token_secret="rc8R5D6DJoIA7vj6Ubz1dPkt3tANLUBJ0xxEzdd2ORWg4")

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

    print("Filter set, creds verified, grabbing stream.")

    start_time = time.time()
    stream = api.GetStreamFilter(track=filters)
    total_tweets = 0

    try:
        tweet = None
        while True:
            tweet = stream.next()

            if tweet:
                total_tweets = total_tweets + 1

                if tweet.get("lang", None) == "en":
                    print tweet["text"]
                    print

                    if tweet.get('created_at') != None:
                        #We have to split out the timezone because python doesn't support %z in 2.7
                        tmp_time = tweet.get('created_at')
                        time_split = tmp_time.split()
                        new_time = time_split[0:-2]
                        new_time.append(time_split[-1])

                        #Turn it back into a string
                        tmp_time = " ".join(new_time)
                        time_conversion = datetime.datetime.strptime(tmp_time, '%a %b %d %H:%M:%S %Y')
                    else:
                        time_conversion = datetime.datetime.now()

                    # message = scrub_message(tweet.get('text'))
                    msg = tweet.get('text')
                    if msg is not None:
                        msg.replace("&amp;", "&")
                        msg.replace("&lt;", "<")
                        msg.replace("&gt;", ">")
                        msg.replace("&quot;", '"')
                        msg.replace("&#39;", "'")
                        msg.replace("&#039", "'")
                        msg.replace("\n", '')
                        msg.replace("\r\n", '')

                    my_tweet = Tweet(
                        message=msg,
                        created_date=time_conversion,
                        twitter_id=tweet.get('id')
                    )

                    if tweet.get('user') != None:
                        my_tweet.username = tweet.get('user').get('screen_name')

                    if tweet.get('in_reply_to_screen_name') != None:
                        my_tweet.in_reply_to_screen_name = tweet.get('in_reply_to_screen_name')

                    if tweet.get('in_reply_to_user_id') != None:
                        my_tweet.in_reply_to_user_id = tweet.get('in_reply_to_user_id')

                    if tweet.get('in_reply_to_status_id') != None:
                        my_tweet.in_reply_to_status_id = tweet.get('in_reply_to_status_id')

                    my_tweet.save()
            else: 
                print("Tweet is none")
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

def scrub_message(message):
    return str(message)

if __name__ == "__main__":
    main()