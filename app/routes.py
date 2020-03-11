from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

# =================================================================
# routes module has the URLs for our app
# in Flask, handlers for the app routes are called *view functions*
# =================================================================

# 2 app decorators:
# creates association between given URL as arg and the following fn.
# So when browser requests either of these URLs,
# Flask invokes the following function

# the index
@app.route('/')
@app.route('/index')
def index():
	# create mock object as a placeholder
	user = {'username': 'Shauna'}
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
		user=user,
		posts=posts)

# add a url ending (route)
# import the form from forms.py
# instantiate a form
# send it to the template to be rendered
@app.route('/login', methods=['GET', 'POST']) # default is GET only
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash("Login requested for user {}, remember_me={}".format(form.username.data, form.remember_me.data))
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form=form)
# can include a link in the nav bar (in base.html)