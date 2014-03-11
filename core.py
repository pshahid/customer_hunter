import logging
from peewee import *
from models import * 
import config

dbconn = MySQLDatabase(config.db, user=config.user, passwd=config.password)

def main():
    setup_logging()
    dbconn.connect()
    Tweet.create_table(fail_silently=True)
    # User.create_table(fail_silently=True)
    Prediction.create_table(fail_silently=True)

def setup_logging():
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRIT': logging.CRITICAL
    }

    level = levels[config.level]
    logging.basicConfig(filename=config.filename, level=level, format=config.format, datefmt=config.datefmt)

if __name__ == "__main__"
	main()