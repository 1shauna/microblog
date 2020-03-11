# The Flask Mega-Tutorial
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# create instance
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
# The bottom import is a workaround to circular imports,
# a common problem with Flask applications.
# You are going to see that the routes module
# needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom
# avoids the error that results from the mutual references
# between these two files.
# ==========================================================


from app import routes, models
# routes module has the URLs for our app
# in Flask, handlers for the app routes are called *view functions*

# models will define the structure of the db
