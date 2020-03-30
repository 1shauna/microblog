import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get("SECRET_KEY") or 'sample-password'

	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	# ==================================================================
	# It is in general a good practice
	# to set configuration from environment variables,
	# and provide a fallback value when the environment
	# does not define the variable.
	# In this case I'm taking the database URL
	# from the DATABASE_URL environment variable,
	# and if that isn't defined,
	# I'm configuring a database named app.db
	# located in the main directory of the application,
	# which is stored in the basedir variable.
	# ==================================================================
	# ==================================================================
	# If an error occurs on the production version of the application,
	# I want to know right away. So my first solution is going to be
	# to configure Flask to send me an email immediately after an error,
	# with the stack trace of the error in the email body.
	# ===================================================================
	MAIL_SERVER = os.environ.get("MAIL_SERVER")
		# if not set, a signal that emailing errors needs to be disabled
	MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
	MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	ADMINS = ['shauna.kerr@gmail.com'] # who will receive error reports

	POSTS_PER_PAGE = 3

	LANGUAGES = ['en', 'fr']
	MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')