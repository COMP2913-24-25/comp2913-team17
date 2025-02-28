from flask import Blueprint

expert_page = Blueprint('expert_page', __name__,
                       template_folder='templates',
                       static_folder='static')

from . import routes
