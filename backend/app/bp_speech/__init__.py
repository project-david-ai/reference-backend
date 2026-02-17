# backend/app/bp_speech/__init__.py
from flask import Blueprint

bp_speech = Blueprint(
    "bp_speech",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/bp_speech/static",
)

from . import routes
