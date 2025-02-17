from flask import Blueprint

dashboard_page = Blueprint('dashboard_page', __name__,
                      template_folder='templates',
                      static_folder='static')

from . import routes
