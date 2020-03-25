# The Flask Mega-Tutorial
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

# create instance
app = Flask(__name__)
app.config.from_object(Config)
# ==========================================================
# One aspect that may seem confusing at first
# is that there are two entities named app.
# The app package is defined by the app directory
# and the __init__.py script,
# and is referenced in the from app import routes statement.
# The app variable is defined as an instance of class Flask
# in the __init__.py script,
# which makes it a member of the app package.
# ==========================================================
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
# The 'login' value is the function (or endpoint) name for the login view.
# In other words, the name you would use in a url_for() call to get the URL.
# ==========================================================
# If a user who is not logged in tries to view a protected page,
# Flask-Login will automatically redirect the user to the login form,
# and only redirect back to the page the user wanted to view
# after the login process is complete.
# For this feature to be implemented, Flask-Login needs to know
# what is the view function that handles logins.
# ==========================================================
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)







# The routes module has the URLs for our app.
# The models will define the structure of the db
from app import routes, models, errors
# =========================================================
# This bottom import is a workaround to circular imports,
# a common problem with Flask applications.
# You are going to see that the routes module
# needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom
# avoids the error that results from the mutual references
# between these two files.
# ==========================================================


if not app.debug: # if app not in debug mode
	if app.config['MAIL_SERVER']: # if app has a mail server
		auth = None
		if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
			auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		secure = None
		if app.config['MAIL_USE_TLS']:
			secure = ()
		mail_handler = SMTPHandler(
			mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
			fromaddr='no-reply@' + app.config['MAIL_SERVER'],
			toaddrs=app.config['ADMINS'], subject='Microblog Failure',
			credentials=auth, secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)
	# In essence, this creates a SMTPHandler instance,
	# sets its level so that it only reports errors and not warnings,
	# informational or debugging messages, and finally attaches it
	# to the app.logger object from Flask.
	if not os.path.exists('logs'):
		os.mkdir('logs')
	file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,backupCount=10)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.setLevel(logging.INFO)
	app.logger.info('Microblog startup')
	# RotatingFileHandler ensures log files don't get too big when app runs
	# for a long time - in this case, size limit of log file is 10KB,
	# and we're keeping the last 10 files as backup.
	# Here, `logging.Formatter` class includes a timestamp, the logging level,
	# the message, and the source file & line number where the log entry originated
	# Also, lowering the logging level to the INFO category
	# (in both app logger and file logger) - choices are:
	# DEBUG, INFO, WARNING, ERROR, CRITICAL - in increasing order of severity.
	# A line is written to log at every server startup (or restart).
