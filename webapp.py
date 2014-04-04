from flask_peewee.auth import Auth
from flask_peewee.admin import Admin
from flask_peewee.db import Database
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from requests_oauthlib import OAuth1Session
from flask_peewee.admin import ModelAdmin
from peewee import *
import config 
import os
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
    fname = CharField()
    lname = CharField()

#Helps pretty print the TwitterUser in the admin
class TwitterUserAdmin(ModelAdmin):
    columns = ('username', 'fname', 'lname')

#flask-peewee auth/admin junk
auth = Auth(webapp, db)
admin = Admin(webapp, auth)

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

# @webapp.route('/stream')
# def stream():
#     return webapp.send_static_file('/Users/paul/repos/customer_hunter/app/static/test.html')

if __name__ == '__main__':
    init_db()
    init_admin()
    webapp.run(port=9000)
# @webapp.route('/static/js/<path:path>')
# def scripts(path):
#     return webapp.send_static_file(os.path.join('/js/', path))

# @webapp.route('/static/css/<path:path>')
# def styles(path):
#     return webapp.send_static_file(os.path.join('/css/', path))

# @webapp.route('/static/fonts/<path:path>')
# def fonts(path):
#     return webapp.send_static_file(os.path.join('/fonts/', path))