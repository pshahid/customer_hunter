from peewee import *
import datetime
import config
from flask_peewee.admin import ModelAdmin
import webapp

   
    # class Meta:
    #     database = MySQLDatabase(config.db, user=config.user, passwd=config.password)


class TwitterUser(webapp.db.Model):
    username = CharField()
    auth_token = CharField()
    auth_secret = CharField()
    fname = CharField(null=True)
    lname = CharField(null=True)

#Helps pretty print the TwitterUser in the admin
class TwitterUserAdmin(ModelAdmin):
    columns = ('username', 'fname', 'lname')