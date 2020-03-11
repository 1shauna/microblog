import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get("SECRET_KEY") or 'sample-password'

	SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	# ========================================================
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
	# ========================================================