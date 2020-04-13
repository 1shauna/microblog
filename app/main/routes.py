from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
	jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm, MessageForm
from app.models import User, Post
from app.translate import translate
from app.main import bp


# Before_request asks that the function be executed right before
# the view function. This is extremely useful because now I can
# insert code that I want to execute before any view function
# in the application, and I can have it in a single place.
# The implementation simply checks if the current_user is logged in,
# and in that case sets the last_seen field to the current time.
@bp.before_request
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
	g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
# If index were a sensitive-info page,
# here is how & where you say you need to be logged in
def index():
	form = PostForm()
	if form.validate_on_submit():
		language = guess_language(form.post.data)
		if language == "UNKNOWN" or len(language) > 5:
			language = ''
		post = Post(body=form.post.data, author=current_user, language=language)
		db.session.add(post)
		db.session.commit()
		flash(_('Your post is now live!'))
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	pages = current_user.followed_posts().paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	posts = pages.items
	next_url = url_for('main.index', page=pages.next_num) \
		if pages.has_next else None
	prev_url = url_for('main.index', page=pages.prev_num) \
		if pages.has_prev else None
	return render_template(
		'index.html',
		title=_('Home'),
		form=form,
		posts=posts,
		pages=pages,
		next_url=next_url,
		prev_url=prev_url
		)

@bp.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type=int)
	pages = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	posts = pages.items
	next_url = url_for('main.explore', page=pages.next_num) \
		if pages.has_next else None
	prev_url = url_for('main.explore', page=pages.prev_num) \
		if pages.has_prev else None
	return render_template('index.html', title=_("Explore"), pages=pages, posts=posts,
						    next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pages = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	posts = pages.items
	next_url = url_for('main.user', username=user.username, page=pages.next_num) \
		if pages.has_next else None
	prev_url = url_for('main.user', username=user.username, page=pages.prev_num) \
		if pages.has_prev else None
	return render_template('user.html', user=user,
							posts=posts, pages=pages,
							next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash(_("Your changes have been saved!"))
		return redirect(url_for('main.edit_profile'))
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



@bp.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(_('User %(x) not found.', x=username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash(_('You cannot follow yourself!'))
		return redirect(url_for('main.user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash(_('You are following %(x)s!', x=username))
	return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(_('User %(x) not found.', x=username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash(_('You cannot unfollow yourself!'))
		return redirect(url_for('main.user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash(_('You are not following %(x)s', x=username))
	return redirect(url_for('main.user', username=username))



@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
	return jsonify({'text': translate(request.form['text'],
									  request.form['source_language'],
									  request.form['dest_language']
									  )
					})

