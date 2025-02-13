from flask import Blueprint

admin_page = Blueprint('admin_page',__name__,
                       template_folder='templates',
                       static_folder='static')

from . import routes