import os
import config
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin, ModelAdmin
from requests_oauthlib import OAuth1Session
from peewee import *
from flask.json import jsonify
import urllib
# import webapp

DATABASE = {
	'name': 'flask_peewee_test',
	'engine': 'peewee.MySQLDatabase',
	'user': config.user,
	'passwd': config.password
}

DEBUG = True
SECRET_KEY = 'wat'

CLIENT_KEY = config.oauth['api_key']
CLIENT_SECRET = config.oauth['api_secret']

webapp = Flask(__name__)
webapp.config.from_object(__name__)

db = Database(webapp)

# webapp.webapp = webapp

class TwitterUser(db.Model):
	username = CharField()
	auth_token = CharField()
	auth_secret = CharField()
	fname = CharField()
	lname = CharField()

#Helps pretty print the TwitterUser in the admin
class TwitterUserAdmin(ModelAdmin):
	columns = ('username', 'fname', 'lname')

auth = Auth(webapp, db)

#This must go after auth's created
admin = Admin(webapp, auth)
admin.register(TwitterUser, TwitterUserAdmin)
auth.register_admin(admin)
admin.setup()

@webapp.route('/')
def index():
	return render_template('index.html', title="Sample Flask App", content="Hello there adventurer!")

@webapp.route('/authed')
@auth.login_required
def auth_area():
	user = auth.get_logged_in_user()

	return "Hello logged in user!"

@webapp.route('/twitter_login')
def auth_to_twitter():
	print request.cookies
	#step 1
	twitter = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri='http://127.0.0.1:5000/callback')
	fetch_response = twitter.fetch_request_token('https://api.twitter.com/oauth/request_token')

	#step 2 Could also be sent to /oauth/authorize
	auth_url = twitter.authorization_url('https://api.twitter.com/oauth/authenticate?force_login=True')

	return redirect(auth_url)

@webapp.route('/callback')
def callback():
	print dir(request)
	#Gotta rebuild the session for step 3
	twitter = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET)
	twitter.parse_authorization_response(request.url)
	#Step 3
	token = twitter.fetch_access_token('https://api.twitter.com/oauth/access_token')

	print(token)

	return "Success, we logged in!"

if __name__ == '__main__':
	auth.User.create_table(fail_silently=True)
	TwitterUser.create_table(fail_silently=True)
	os.environ['DEBUG'] = "1"

	webapp.run(debug=True)