from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
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

