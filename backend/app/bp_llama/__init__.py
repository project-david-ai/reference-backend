#backend/app/bp_gpt/__init__.py
from flask import Blueprint

bp_llama = Blueprint(
    'bp_llama', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/bp_llama/static'

)

from . import routes