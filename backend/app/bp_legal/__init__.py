# bp_identy/__init__.py
from flask import Blueprint

bp_legal = Blueprint(
    "bp_legal",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/bp_legal/static",
)

from . import routes
