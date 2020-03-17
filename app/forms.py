from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField("Sign In")
# These fields know hot to render themselves as HTML!
# But other things can't:
# See the login template.

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	# Email() ensures an email structure is used
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password',
		validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')
	#=====================================================================
	# validate_username() and validate_email()
	# When you add any methods that match the pattern
	# validate_<field_name>, WTForms takes those as custom validators
	# and invokes them in addition to the stock validators.
	# In this case I want to make sure that the username and email
	# address entered by the user are not already in the database,
	# so these two methods issue database queries expecting there
	# will be no results. In the event a result exists,
	# a validation error is triggered by raising ValidationError.
	# ====================================================================


class EditProfileForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
	submit = SubmitField("Submit")

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
				raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
	post = TextAreaField("Say something",
		validators=[DataRequired(), Length(min=1, max=140)])
	submit = SubmitField('Submit')
