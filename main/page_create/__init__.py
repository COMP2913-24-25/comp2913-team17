from flask import Blueprint

create_page = Blueprint('create_page', __name__,
                      template_folder='templates',
                      static_folder='static')

from . import routes
