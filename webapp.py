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
    'user': config.user,
    'passwd': config.password
}

webapp = Flask(__name__)
webapp.config.from_object(__name__)

db = Database(webapp)

#flask-peewee auth/admin junk
auth = Auth(webapp, db)
admin = Admin(webapp, auth)

# class MySQLModel(db.Model):
#     class Meta:
#         database = MySQLDatabase('social_consumer', user=config.user, passwd=config.password)

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
    return render_template('index.html', title="ML Systems")

@webapp.route('/home')
@auth.login_required
def home():
    user = auth.get_logged_in_user()

    if user is not None:
        return render_template('auth_main.html', username=user.username, local=config.debug)

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

    return render_template('social_account.html', username=user.username, accounts=twitter_accounts)

@webapp.route('/account')
@auth.login_required
def account():
    user = auth.get_logged_in_user()
    try:
        acct = auth.User.get(auth.User.id == user.id)
    except DoesNotExist:
        print "User does not exist"
    else:
        return render_template('account.html', title='ML Account', account=acct, user=user, username=user.username)

@webapp.route('/change_acct_cred', methods=['POST', 'GET'])
@auth.login_required
def change_cred():
    user = auth.get_logged_in_user()
    try:
        acct = auth.User.get(auth.User.id == user.id)

        if request.method == 'POST':
            change_acct_cred(request.form, user)

    except DoesNotExist:
        print "User doesn't exist...you shouldn't be seeing this often"
    finally:
        return redirect('account')

def change_acct_cred(form, user):
    #Don't do anything if the user is None or False
    if user:
        change_password(user, form['old_password'], form['new_password'], form['confirm_new_password'])
        change_username(user, form['username'])
        change_email(user, form['new_email'])

        user.save()

def change_password(user, old, new, confirm):
    if len(old) > 0:
        usr = auth.authenticate(user.username, old)

        if len(new) > 0 and usr:
            if new == confirm and new != old:
                user.set_password(new)

def change_username(user, new):
    if user:
        if user.username != new:
            try:
                auth.User.get(auth.User.username == new)
            except DoesNotExist:
                #This is good, we want this
                user.username = new

def change_email(user, email):
    if user:
        if user.email != email and len(email) > 0:
            try:
                auth.User.get(auth.User.email == email)
            except DoesNotExist:
                user.email = email

@webapp.route('/twitter_login')
@auth.login_required
def auth_to_twitter():
    #step 1
    twitter = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri=config.callback_uri)
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
    mluser = auth.get_logged_in_user()

    try:
        twitter_id= token['user_id']
        
        user = TwitterUser.get(TwitterUser.twitter_id == twitter_id)
        user.auth_token = token['oauth_token']
        user.auth_secret = token['oauth_token_secret']
        user.ml_user = mluser
        user.save()
    except DoesNotExist:
        user = TwitterUser(username=token['screen_name'], twitter_id=token['user_id'], auth_secret=token['oauth_token_secret'], auth_token=token['oauth_token'], ml_user=mluser.id)
        user.save()

    return render_template('auth_main.html', username=mluser.username, local=config.debug)

if __name__ == '__main__':
    init_db()
    init_admin()
    webapp.run(port=5000, debug=True)
