import csv
import sys
from peewee import *
# from models import *
import argparse
import sys

print sys.path
sys.exit(0)
dbconn = MySQLDatabase("social_consumer", user="root")
dbconn.connect()

def read_from_db(fname, start_id=0, total=-1):
    total = total
    start_id = start_id

    rows = []

    with open(fname, "w") as f:
        csv_writer = csv.writer(f, dialect='excel')

        iterator = None

        if total > -1:
            iterator = Tweet.select().where( (Tweet.id>=start_id) & (Tweet.id < (Tweet.id + total))).iterator()
        else:
            iterator = Tweet.select().where((Tweet.id>=start_id)).iterator()
        
        for tweet in iterator:
            row = []
            row.append('')
            row.append(tweet.message.encode('ascii', 'ignore'))
            row.append(tweet.id)

            csv_writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Write MySQL rows out to CSV files.')
    parser.add_argument('-s', '--start_id', action='store', type=int, help="Tweet ID to start with in the DB", required=False)
    parser.add_argument('-t', '--total',action='store', type=int,help="How many rows to write", required=False)
    args = parser.parse_args()

    #Not trying to be clever, but **vars(args) converts args to a dict then expands it in-place
    read_from_db("tweet.csv", **vars(args))