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
        
        for tweet in Tweet.select():
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
            rows.append(row)
            count = count + 1

            if count % 1000 == 0:
                count = 0
                csv_writer.writerows(rows)
                rows = []

        if len(rows) > 0:
            csv_writer.writerows(rows)

if __name__ == "__main__":
    read_from_db("tweet.csv")