from peewee import *
# from app import dbconn
import datetime
import config

class MySQLModel(Model):
    def __str__(self):
        r = {}
        for k in self._data.keys():
          try:
             r[k] = str(getattr(self, k))
          except:
             r[k] = json.dumps(getattr(self, k))
        return str(r)
    
    class Meta:
        database = MySQLDatabase(config.db, user=config.user, passwd=config.password)
        # database = dbconn

class User(MySQLModel):
    username = CharField()

class Tweet(MySQLModel):
    # user = ForeignKeyField(User, related_name='tweets', null=True)
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now())
    twitter_id = BigIntegerField(default=None, null=True)
    in_reply_to_user_id = BigIntegerField(default=-1, null=True)
    in_reply_to_screen_name = CharField(default=-1, null=True)
    in_reply_to_status_id = BigIntegerField(default=-1, null=True)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)
    username = CharField()
    logit_prediction = BigIntegerField(default=-1)
    sgd_prediction = BigIntegerField(default=-1)
