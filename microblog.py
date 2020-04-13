from app import create_app, db, cli
from app.models import User, Post

# actually initialize the app!
app = create_app()
cli.register(app)

# create a shell context
# add the db instance and models (User, Post) to the shell session
@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'User': User, 'Post': Post}