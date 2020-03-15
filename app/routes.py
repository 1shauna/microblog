from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime

# =================================================================
# The routes module has the URLs for our app
# in Flask, handlers for the app routes are called *view functions*
# =================================================================

# ================================================================
# App decorators: are the @app stuff
# Decorators create association between given URL as arg
# and the following function. When browser requests either of these URLs,
# Flask invokes the following function
#===================================================================

# the index
@app.route('/')
@app.route('/index')
@login_required
# If index were a sensitive-info page,
# here is how & where you say you need to be logged in
def index():
	posts = [
		{
			'author': {'username': 'Authoress'},
			'body': 'Beautiful Montreal Day!'
		},
		{
			'author': {'username': 'Jolanda'},
			'body': 'The Avengers movie was so cool!'
		}]
	return render_template(
		'index.html',
		title='HomeAlone',
		posts=posts)


# add a url ending (route)
# import the form from forms.py
# instantiate a form
# send it to the template to be rendered
@app.route('/login', methods=['GET', 'POST']) # default is GET only
def login():
	# current_user is from Flask-Login and gets the user object
	# that represents the client of the request
	if current_user.is_authenticated:
		# already logged in, so redirect!
		return redirect(url_for('index'))

	form = LoginForm()

	if form.validate_on_submit():
		# .first() returns the first item since there's only 1 or no items
		user = User.query.filter_by(username=form.username.data).first()

		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password!')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		# =============================================================
		# When a user that is not logged in accesses a view function
		# protected with the @login_required decorator, the decorator
		# is going to redirect to the login page, but it is going to
		# include some extra information in this redirect so that
		# the application can then return to the first page. If the user
		# navigates to /index, for example, the @login_required decorator
		# will intercept the request and respond with a redirect
		# to /login, but it will add a query string argument to this URL,
		# making the complete redirect URL /login?next=/index.
		# =============================================================
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			# (1) if login URL doesn't have a `next` argument
			# or
			# (2) if login URL has this, but it includes a domain name
			# then redirected to `index`
			# Case 2 ensures redirect remains within same site
			next_page = url_for('index')
		# (3) if login URL includes a `next` arg that's set to a relative path
		# (ie. without a domain portion)
		# then redirected to the `next` page
		return redirect(next_page)

	return render_template('login.html', title='Sign In', form=form)
# can include a link in the nav bar (in base.html)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	# check that user not already logged in
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Conngratulations, you are now a registered user!!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)



@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
		{'author': user, 'body': 'Test post #1'},
		{'author': user, 'body': 'Test post #2'}
	]
	return render_template('user.html', user=user, posts=posts)



# Before_request asks that the function be executed right before
# the view function. This is extremely useful because now I can
# insert code that I want to execute before any view function
# in the application, and I can have it in a single place.
# The implementation simply checks if the current_user is logged in,
# and in that case sets the last_seen field to the current time.
@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
	# If you are wondering why there is no db.session.add() before the commit,
	# consider that when you reference current_user, Flask-Login will invoke
	# the user loader callback function, which will run a database query
	# that will put the target user in the database session.
	# So you can add the user again in this function,
	# but it is not necessary because it is already there.


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash("Your changes have been saved!")
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)
	# 1) info validated so profile is changed.
	# 2) info not validated but:
	# 2a) browser sent GET request -
	# --> return an initial version of the form template (pre-populated fields
	# with info stored in the db)
	# 2b) browser sent POST request but something is invalid -
	# --> in this validation-error case, don't want to write anything
	# to the form fields since they should already be populated by WTForms.
	#