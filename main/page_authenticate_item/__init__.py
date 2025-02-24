from flask import Blueprint

authenticate_item_page = Blueprint('authenticate_item_page', __name__,
                      template_folder='templates',
                      static_folder='static')

from . import routes
