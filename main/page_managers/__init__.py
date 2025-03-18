from flask import Blueprint

manager_page = Blueprint('manager_page', __name__,
                       template_folder='templates',
                       static_folder='static')

from . import routes
