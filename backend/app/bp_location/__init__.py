#backend/app/bp_location/__init__.py
from flask import Blueprint

bp_location = Blueprint(
    'bp_location', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/bp_location/static'
)

from . import routes