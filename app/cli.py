from app import app
import click
import os


# to create custom flask command line commands!
# from Click:  http://click.pocoo.org/5/


@app.cli.group()
def translate():
	"""Translation and localization commands."""
	pass
	# The name of the command comes from the name of the decorated function,
	# and the help message comes from the docstring. Since this is a parent
	# command that only exists to provide a base for the sub-commands,
	# the function itself does not need to do anything.


@translate.command()
def update():
	"""Update all languages."""
	if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
		raise RuntimeError('extract command failed')
	if os.system('pybabel update -i messages.pot -d app/translations'):
		raise RuntimeError('update command failed')
	os.remove('messages.pot')

@translate.command()
def compile():
	"""Compile all languages."""
	if os.system('pybabel compile -d app/translations'):
		raise RuntimeError('compile command failed')

# ======================================================================
# Note how the decorator from these functions is derived from the translate
# parent function. This may seem confusing, since translate() is a function,
# but it is the standard way in which Click builds groups of commands.
# Same as with the translate() function, the docstrings for these functions
# are used as help message in the --help output.
#
# You can see that for all commands, I run them and make sure that
# the return value is zero, which implies that the command did not return
# any error. If the command errors, then I raise a RuntimeError,
# which will cause the script to stop. The update() function combines
# the extract and update steps in the same command, and if everything
# is successful, it deletes the messages.pot file after the update
# is complete, since this file can be easily regenerated when needed again.
# =======================================================================


@translate.command()
@click.argument('lang')
def init(lang):
	"""Initialize a new language."""
	if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
		raise RuntimeError('extract command failed')
	if os.system(
		'pybabel init -i messages.pot -d app/translations -l ' + lang):
		raise RuntimeError('init command failed')
	os.remove('messages.pot')
