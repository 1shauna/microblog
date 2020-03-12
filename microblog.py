from app import app, db
from app.models import User, Post

# create a shell conntext
# add the db instance and models (User, Post) to the shell session
@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'User': User, 'Post': Post}