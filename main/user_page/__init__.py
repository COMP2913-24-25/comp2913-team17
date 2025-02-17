from flask import Blueprint

user_page = Blueprint('user_page', __name__,
                      template_folder='templates',
                      static_folder='static')

from . import routes
