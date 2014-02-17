import csv
from peewee import *
from models import *

dbconn = MySQLDatabase("social_consumer", user="root")
dbconn.connect()

rows = []

def write_to_file(fname):
	read_from_db()
	with open(fname, "w") as f:
		csv_writer = csv.writer(f, dialect='excel')
			# csv_writer.writerows(rows)
	# print rows
	# csv_writer.writerow("id,message,created_date,twitter_id,in_reply_to_user_id,in_reply_to_screen_name,in_reply_to_status_id,latitude,longitude,username")
		csv_writer.writerows(rows) 
	# del f

def read_from_db():
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

if __name__ == "__main__":
	write_to_file("tweet.csv")