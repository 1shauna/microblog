from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers


# if you want the errors templates to be in errors/ rather than errors/templates/,
# then you add a `template_folder='templates'` argument to the Blueprint()
# constructor.