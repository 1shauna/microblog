from flask import render_template
from app import db
from app.errors import bp

# We can use custom error pages!

@bp.app_errorhandler(404)
def not_found_error(error):
	return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('errors/500.html'), 500
	# I'm returning the contents of their respective templates.
	# Note that both functions return a second value after the template,
	# which is the error code number. Since these are error pages,
	# I want the status code of the response to reflect that.
