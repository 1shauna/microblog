# The Flask Mega-Tutorial
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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







# The routes module has the URLs for our app.
# The models will define the structure of the db
from app import routes, models
# =========================================================
# This bottom import is a workaround to circular imports,
# a common problem with Flask applications.
# You are going to see that the routes module
# needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom
# avoids the error that results from the mutual references
# between these two files.
# ==========================================================


