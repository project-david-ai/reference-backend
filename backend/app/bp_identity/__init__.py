# bp_identy/__init__.py
from flask import Blueprint

bp_identity = Blueprint(
    "bp_identity",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/bp_identity/static",
)

from . import routes
