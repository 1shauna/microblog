from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

# Since this is an auxiliary table that has no data other than
# the foreign keys, it's created without an associated model class.
followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


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
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)

	# `followed` is from the point of view of the left side of relationship tables
	followed = db.relationship(
		'User', # right side of relationship (users)
		secondary=followers, # left side of relationship (followers)
		primaryjoin=(followers.c.follower_id == id), # condition that links the left with the association table
		secondaryjoin=(followers.c.followed_id == id), # condition that links the right with the association table
		backref=db.backref('followers', lazy='dynamic'), # how this relationship will be accessed from the right side (from the left, the relationship is named `followed`)
		lazy='dynamic')
	# =====================================================================
	# `db.relationship` function defines the relationship in the model class.
	# This relationship links User instances to other User instances,
	# so as a convention let's say that for a pair of users linked by
	# this relationship, the left side user is following the right side user.
	# I'm defining the relationship as seen from the left side user with
	# the name followed, because when I query this relationship from
	# the left side I will get the list of followed users
	# (i.e those on the right side).
	#
	# 'User' is the right side entity of the relationship
	# (the left side entity is the parent class). Since this is
	# a self-referential relationship, I have to use the same class
	# on both sides.
	# Secondary configures the association table that is used
	# for this relationship, which I defined right above this class.
	# primaryjoin indicates the condition that links the left side entity
	# (the follower user) with the association table.
	# The join condition for the left side of the relationship is
	# the user ID matching the follower_id field of the association table.
	# The followers.c.follower_id expression references the follower_id
	# column of the association table.
	# secondaryjoin indicates the condition that links the right side entity
	# (the followed user) with the association table. This condition
	# is similar to the one for primaryjoin, with the only difference
	# that now I'm using followed_id, which is the other foreign key in
	# the association table.
	# backref defines how this relationship will be accessed from
	# the right side entity. From the left side, the relationship
	# is named followed, so from the right side I am going to use
	# the name followers to represent all the left side users that
	# are linked to the target user in the right side. The additional
	# lazy argument indicates the execution mode for this query.
	# A mode of dynamic sets up the query to not run until specifically
	# requested, which is also how I set up the posts one-to-many relationship.
	# Lazy is similar to the parameter of the same name in the backref,
	# but this one applies to the left side query instead of the right side.
	# =====================================================================


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

	def avatar(self, size):
		# encoded as byes before passing to hash function
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
	# ===============================================================
	# The nice thing about making the User class responsible
	# for returning avatar URLs is that if some day I decide
	# Gravatar avatars are not what I want, I can just rewrite
	# the avatar() method to return different URLs, and all the templates
	# will start showing the new avatars automatically.
	# ================================================================

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id
			).count() > 0

	# in order to display recent posts by authors that current_user follows:
	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())
		# `followed` is queried on the Posts table: join the followers table
		# on followers.followed_id == Post.user_id.
		# Then filter where the follower's id is the current_user's id.
		# `own` is the user's own posts, because apparently users (evwhere)
		# like to see their own posts on their followed posts. Dunno.
		# Then join these 2 queries with union,
		# and order by the post's timestamp, descending (most recent)

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm="HS256").decode('utf-8')
		# jwt.encode() returns a byte sequence, so decode it

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			# if cannot be validated, or is expired
			return
		return User.query.get(id)



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

