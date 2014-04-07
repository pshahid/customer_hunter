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

class TwitterUser(db.Model):
    username = CharField()
    auth_token = CharField()
    auth_secret = CharField()
    twitter_id = BigIntegerField()
    fname = CharField(null=True, default="")
    lname = CharField(null=True, default="")

#Helps pretty print the TwitterUser in the admin
class TwitterUserAdmin(ModelAdmin):
    columns = ('username', 'fname', 'lname')

#flask-peewee auth/admin junk
auth = Auth(webapp, db)
admin = Admin(webapp, auth)

class SignInForm(Form):
    email = wtforms.TextField(validators=[validators.Length(min=6, max=35)])
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

@webapp.route('/authed')
@auth.login_required
def auth_area():
    user = auth.get_logged_in_user()

    return "Hello logged in user!"

@webapp.route('/login', methods=['GET', 'POST'])
def login():
    form = SignInForm(request.form)

    if request.method == 'POST' and form.validate():
        return render_template('auth_main.html', username=request.form['email'], local=True)

    return render_template('login.html', form=form)

@webapp.route('/logout')
def logout():
    return render_template('index.html', title='ML Systems')

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
    #Gotta rebuild the session for step 3
    twitter = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET)
    twitter.parse_authorization_response(request.url)
    #Step 3
    token = twitter.fetch_access_token('https://api.twitter.com/oauth/access_token')

    try:
        twitter_id= token['user_id']
        
        user = TwitterUser.get(TwitterUser.twitter_id == twitter_id)

        user.auth_token = token['oauth_token']
        user.auth_secret = token['oauth_token_secret']
        user.save()
        content='Welcome back, ' + token['screen_name']
    except DoesNotExist:
        user = TwitterUser(username=token['screen_name'], twitter_id=token['user_id'], auth_secret=token['oauth_token_secret'], auth_token=token['oauth_token'])
        user.save()
        content = 'Welcome to ML Systems, you\'ve added ' + token['screen_name'] + ' as a Twitter account.'

    return render_template('index.html', title='Logged in', content=content)

if __name__ == '__main__':
    init_db()
    init_admin()
    webapp.run(port=5000, debug=True)
