from flask import Blueprint

bp_auth = Blueprint(
    'bp_auth', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/bp_auth/static')

from . import routes

