import csv
from peewee import *
from models import *

dbconn = MySQLDatabase("social_consumer", user="root")
dbconn.connect()

def read_from_db(fname):
    count = 0
    rows = []

    with open(fname, "w") as f:
        csv_writer = csv.writer(f, dialect='excel')

        for i in range(Tweet.select().count()):
            tq = Tweet.select().where(Tweet.id == i).limit(1).execute()
            for tweet in tq:
                row = []
                row.append(tweet.id)
                row.append(tweet.message.encode('ascii', 'ignore'))
                row.append(tweet.created_date)
                row.append(tweet.twitter_id)
                row.append(tweet.in_reply_to_user_id)
                row.append(tweet.in_reply_to_screen_name)
                row.append(tweet.in_reply_to_status_id)
                row.append(tweet.latitude)
                row.append(tweet.longitude)
                row.append(tweet.username)

                csv_writer.writerow(row)

if __name__ == "__main__":
    read_from_db("tweet.csv")