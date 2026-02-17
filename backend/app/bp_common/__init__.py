# backend/app/bp_common/__init__.py
from flask import Blueprint

bp_common = Blueprint(
    "bp_common",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/bp_common/static",
)

from . import routes
