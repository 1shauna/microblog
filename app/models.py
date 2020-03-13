from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
	""" fields:
	id INTEGER primary key
	username VARCHAR (64)
	email VARCHAR (120)
	password_hash VARCHAR (128)
	"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	# posts added with the Post class
	# and we need a new db migration (and upgrade)
	# since the db already exists
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	# =======================================================
	# The User class has a new posts field, that is initialized
	# with db.relationship. This is not an actual database field,
	# but a high-level view of the relationship between users
	# and posts, and for that reason it isn't in the database
	# diagram. For a one-to-many relationship, a db.relationship
	# field is normally defined on the "one" side,
	# and is used as a convenient way to get access to the "many".
	# So for example, if I have a user stored in u,
	# the expression u.posts will run a database query
	# that returns all the posts written by that user.
	# The first argument to db.relationship is the model class
	# that represents the "many" side of the relationship.
	# This argument can be provided as a string
	# with the class name if the model is defined later
	# in the module. The backref argument defines the name
	# of a field that will be added to the objects
	# of the "many" class that points back at the "one" object.
	# This will add a post.author expression that will return
	# the user given a post. The lazy argument defines how
	# the database query for the relationship will be issued.
	# =======================================================

	def __repr__(self):
		return '<User {}>'.format(self.username)
	# ===========================================================
	# The __repr__ method tells Python how to print objects
	# of this class, which is going to be useful for debugging.
	# You can see the __repr__() method in action
	# in the Python interpreter session below:
	#
	# >>> from app.models import User
	# >>> u = User(username='susan', email='susan@example.com')
	# >>> u
	# <User susan>
	# ============================================================

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

# command line: flask db init
# ==============================================================
# With the migration repository in place, it is time
# to create the first database migration,
# which will include the users table that maps
# to the User database model. There are two ways
# to create a database migration: manually or automatically.
# To generate a migration automatically,
# Alembic compares the database schema as defined
# by the database models, against the actual database schema
# currently used in the database. It then populates the migration
# script with the changes necessary to make the database schema
# match the application models. In this case,
# since there is no previous database,
# the automatic migration will add the entire User model
# to the migration script. The flask db migrate sub-command
# generates these automatic migrations:
#
# flask db migrate -m "users table"
#
# the comment given with the -m option is optional;
# it adds a short descriptive text to the migration
#
# the `flask db migrate` command DOES NOT MAKE ANY CHANGES
# to the db; it just generates the migration script.
# To apply the changes, you must use `flask db upgrade`
# ==============================================================
# Note that Flask-SQLAlchemy uses a "snake case"
# naming convention for database tables by default.
# For the User model above, the corresponding table
# in the database will be named user.
# For a AddressAndPhone model class, the table would
# be named address_and_phone. If you prefer to choose
# your own table names, you can add an attribute
# named __tablename__ to the model class,
# set to the desired name as a string.
# ==============================================================

# blog posts
class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	# timestamp will be indexed so can retrieve in chrono order
	# Also, datetime.utcnow is a function -
	# it is passed in TO BE CALLED at that time. NOT NOW.
	# Also, utc ensures uniform timestamps, regardless where users are located
	# and will be converted to the user's local time when displayed.
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

# keeps track of a user's "logged-in-ness"
@login.user_loader
def load_user(id):
	return User.query.get(int(id))