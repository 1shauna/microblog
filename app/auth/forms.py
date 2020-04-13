from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l, _
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
	username = StringField(_l('Username'), validators=[DataRequired()])
	password = PasswordField(_l("Password"), validators=[DataRequired()])
	remember_me = BooleanField(_l('Remember Me'))
	submit = SubmitField(_l("Sign In"))
# These fields know hot to render themselves as HTML!
# But other things can't:
# See the login template.

class RegistrationForm(FlaskForm):
	username = StringField(_l('Username'), validators=[DataRequired()])
	email = StringField(_l('Email'), validators=[DataRequired(), Email()])
	# Email() ensures an email structure is used
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	password2 = PasswordField(
		_l('Repeat Password'),
		validators=[DataRequired(), EqualTo(_l('password'))])
	submit = SubmitField(_l('Register'))

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError(_l('Please use a different username.'))

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError(_l('Please use a different email address.'))
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

class ResetPasswordRequestForm(FlaskForm):
	email = StringField(_('Email'), validators=[DataRequired(), Email()])
	submit = SubmitField(_('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	password2 = PasswordField(
		_('Repeat Password'), validators=[DataRequired(), EqualTo(_('password'))])
	submit = SubmitField(_('Request Password Reset'))