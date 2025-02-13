from flask import Blueprint

item_page = Blueprint('item_page', __name__,
                      template_folder='templates',
                      static_folder='static')

from . import routes