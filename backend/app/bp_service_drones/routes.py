from flask import jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required
from backend.app.services.logging_service.logger import LoggingUtility

from . import bp_service_drones


@bp_service_drones.route('/api/thread/meta', methods=['GET'])
@jwt_required()
def update_thread_meta():

    pass