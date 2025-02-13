from flask import Blueprint

bidding_page = Blueprint('bidding_page', __name__,
                         template_folder='templates',
                         static_folder='static')

from . import routes