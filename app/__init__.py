# The Flask Mega-Tutorial
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os




## ============
## Globals
## ============
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
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
mail = Mail()
moment = Moment()
bootstrap = Bootstrap()
babel = Babel()


# create instance
def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)
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

	db.init_app(app)
	migrate.init_app(app, db)
	login.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	bootstrap.init_app(app)
	babel.init_app(app)
	# ===========================================================
	# Here, we initiate the app inside a function, so that we can have multiple
	# iterations, such as when we're testing and etc. This way we can test (ie)
	# on a separate instance than the original. If any changes are made,
	# then we make them, and re-initiate to test.
	## When we do this, we init globally WITHOUT the app arguments,
	## and initiate inside the function WITH the app arguments.
	# ===========================================================

	from app.errors import bp as errors_bp
	app.register_blueprint(errors_bp)

	from app.auth import bp as auth_bp
	app.register_blueprint(auth_bp, url_prefix='/auth')

	from app.main import bp as main_bp
	app.register_blueprint(main_bp)

	# from app.api import bp as api_bp
	# app.register_blueprint(api_bp, url_prefix='/api')

	if not app.debug and not app.testing: # if app not in debug or testing mode
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
				toaddrs=app.config['ADMINS'], subject=_l('Microblog Failure'),
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
	return app


@babel.localeselector
def get_locale():
	return request.accept_languages.best_match(current_app.config['LANGUAGES'])


# The models will define the structure of the db
from app import models
# =========================================================
# This bottom import is a workaround to circular imports,
# a common problem with Flask applications.
# You are going to see that the routes module
# needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom
# avoids the error that results from the mutual references
# between these two files.
# ==========================================================