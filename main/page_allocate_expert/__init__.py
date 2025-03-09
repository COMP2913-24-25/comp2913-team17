from flask import Blueprint

# Create the blueprint
allocate_expert_bp = Blueprint('allocate_expert', __name__, template_folder="templates")

# Import the routes
from .routes import *
