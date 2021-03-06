from __future__ import print_function
'''
Include all imports in this file; it will be called at the beginning of all files.
'''
# We need a bunch of Flask stuff
from flask import *
import pprint
from app import models
from models import *                # all the database models
from app.logic.switch import switch # implements switch/case statements
from flask_security import Security, PeeweeUserDatastore
import os.path as op
from flask_mail import Mail

''' Creates an Flask object; @app will be used for all decorators.
from: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
"A decorator is just a callable that takes a function as an argument and 
returns a replacement function. See start.py for an example"
'''

app = Flask(__name__)
cfg = load_config('config/config.yaml')

# Flask configuration: 
app.config.update(  SECRET_KEY = cfg['flask']['secret_key'],
                    DEBUG = cfg['flask']['debug'],
                    SECURITY_PASSWORD_HASH = cfg['flask_security']['security_password_hash'],
                    SECURITY_PASSWORD_SALT= cfg['flask_security']['security_password_salt'])
                    
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'username'
app.config['MAIL_PASSWORD'] = 'password'
mail = Mail(app)

db = SqliteDatabase(cfg['databases']['dev'])

# Setup Flask-Security    
user_datastore = PeeweeUserDatastore(db, User, Role, UserRole)
security = Security(app, user_datastore)

# This processor is added to all templates
@security.context_processor
def security_context_processor():
    return dict(hello="world")

# This processor is added to only the register view
@security.register_context_processor
def security_register_processor():
    return dict(something="else")
    
# This processor is added to all emails
@security.mail_context_processor
def security_mail_processor():
    return dict(hello="world")

path = op.join(op.dirname(__file__), 'static/files/uploads')

# Builds all the database connections on app run
# Don't panic, if you need clarification ask.

@app.before_request
def before_request():
    g.dbMain =  db.connect()

@app.teardown_request
def teardown_request(exception):
    dbM = getattr(g, 'db', None)
    if (dbM is not None) and (not dbM.is_closed()):
      dbM.close()
