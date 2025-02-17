from flask import Blueprint

auth_page = Blueprint('auth_page', __name__,
                       template_folder='templates',
                       static_folder='static')

from . import routes
