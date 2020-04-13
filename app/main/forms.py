
from flask import request
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l, _
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User



class EditProfileForm(FlaskForm):
	username = StringField(_l("Username"), validators=[DataRequired()])
	about_me = TextAreaField(_l("About me"), validators=[Length(min=0, max=140)])
	submit = SubmitField(_l("Submit"))

	# =======================================================================
	# During registration, I need to make sure the username entered
	# in the form does not exist in the database. On the edit profile form
	# I have to do the same check, but with one exception. If the user
	# leaves the original username untouched, then the validation should
	# allow it, since that username is already assigned to that user.
	# =======================================================================
	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError(_l('Please use a different username.'))


class PostForm(FlaskForm):
	post = TextAreaField(_("Say something"),
		validators=[DataRequired(), Length(min=1, max=140)])
	submit = SubmitField(_('Submit'))

class SearchForm(FlaskForm):
	pass

class MessageForm(FlaskForm):
	pass