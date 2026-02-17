# backend/app/bp_service_drones/__init__.py
from flask import Blueprint

bp_service_drones = Blueprint(
    "bp_service_drones",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/bp_common/static",
)

from . import routes
