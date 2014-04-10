from flask_peewee.auth import Auth
from flask_peewee.admin import Admin
from flask_peewee.db import Database
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from wtforms import Form, validators
import wtforms
from requests_oauthlib import OAuth1Session
from flask_peewee.admin import ModelAdmin
from peewee import *
import config 
import os
import sys
# import flask_models

SECRET_KEY = 'wasdfasdfat'

CLIENT_KEY = config.oauth['api_key']
CLIENT_SECRET = config.oauth['api_secret']

os.environ['DEBUG'] = "1"

DATABASE = {
    'name': 'social_consumer',
    'engine': 'peewee.MySQLDatabase',
    'user': 'root',
    'passwd': ''
}

webapp = Flask(__name__)
webapp.config.from_object(__name__)

db = Database(webapp)

#flask-peewee auth/admin junk
auth = Auth(webapp, db)
admin = Admin(webapp, auth)

class TwitterUser(db.Model):
    username = CharField()
    auth_token = CharField()
    auth_secret = CharField()
    twitter_id = BigIntegerField()
    email = CharField(null=True)
    fname = CharField(null=True, default="")
    lname = CharField(null=True, default="")
    ml_user = ForeignKeyField(auth.User) 

#Helps pretty print the TwitterUser in the admin
class TwitterUserAdmin(ModelAdmin):
    columns = ('username', 'fname', 'lname')

class SignInForm(Form):
    username = wtforms.TextField(validators=[validators.Length(min=2, max=35)])
    password = wtforms.PasswordField('Password', [validators.Required()])


def init_admin():
    admin.register(TwitterUser, TwitterUserAdmin) #Register the admin nonsense for flask-peewee
    auth.register_admin(admin)
    admin.setup()

def init_db():
    TwitterUser.create_table(fail_silently=True)
    auth.User.create_table(fail_silently=True)

@webapp.errorhandler(404)
def not_found(error):
    return "404 -- that's a paddlin'"

@webapp.route('/')
def index():
    return render_template('index.html', title="Sample Flask App", content="Hello there adventurer!")

@webapp.route('/home')
@auth.login_required
def home():
    user = auth.get_logged_in_user()

    if user is not None:
        return render_template('auth_main.html', username=user.username, local=True)

@webapp.route('/logout')
def logout():
    return render_template('index.html', title='ML Systems')

@webapp.route('/addtwitter')
@auth.login_required
def add_twitter():
    user = auth.get_logged_in_user()
    accounts = TwitterUser.select().where(TwitterUser.ml_user == user.id)
    twitter_accounts = []

    for acc in accounts:
        twitter_accounts.append(acc)

    return render_template('account.html', username=user.username, accounts=twitter_accounts)

@webapp.route('/twitter_login')
@auth.login_required
def auth_to_twitter():
    print request.cookies
    #step 1
    twitter = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri='http://127.0.0.1:5000/callback')
    fetch_response = twitter.fetch_request_token('https://api.twitter.com/oauth/request_token')

    #step 2 Could also be sent to /oauth/authorize
    auth_url = twitter.authorization_url('https://api.twitter.com/oauth/authenticate?force_login=True')

    return redirect(auth_url)

@webapp.route('/callback')
@auth.login_required
def callback():
    #Gotta rebuild the session for step 3
    twitter = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET)
    twitter.parse_authorization_response(request.url)
    #Step 3
    token = twitter.fetch_access_token('https://api.twitter.com/oauth/access_token')

    try:
        twitter_id= token['user_id']
        
        user = TwitterUser.get(TwitterUser.twitter_id == twitter_id)
        mluser = auth.get_logged_in_user()
        user.auth_token = token['oauth_token']
        user.auth_secret = token['oauth_token_secret']
        user.ml_user = mluser
        user.save()
    except DoesNotExist:
        mluser = auth.get_logged_in_user()
        print mluser
        user = TwitterUser(username=token['screen_name'], twitter_id=token['user_id'], auth_secret=token['oauth_token_secret'], auth_token=token['oauth_token'], ml_user=mluser.id)
        user.save()

    return render_template('auth_main.html', username=user.username, local=True)

if __name__ == '__main__':
    init_db()
    init_admin()
    webapp.run(port=5000, debug=True)
