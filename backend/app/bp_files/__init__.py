#backend/app/bp_files/__init__.py
from flask import Blueprint

bp_files = Blueprint(
    'bp_files', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/bp_files/static'
)

from . import routes