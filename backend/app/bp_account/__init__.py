#bp_identy/__init__.py
from flask import Blueprint

bp_account = Blueprint(
    'bp_account', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/bp_account/static'
)

from . import routes