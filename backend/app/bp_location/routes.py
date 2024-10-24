from backend.app.services.logging_service.logger import LoggingUtility
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import bp_location

logging_utility = LoggingUtility()


@bp_location.route('/3vzFLKUZLX9vW7ZmNF0zrVVOxJ4AJPV7x8AKatQMX8KCucDanC5SnfyGexElLPc2GUb60iAQvzOT2NTmnrryCHcW31BekpEduXip', methods=['POST'])
@jwt_required()
def update_current_user_location():
    logging_utility.info("Received request to update current user location")

    authorization_header = request.headers.get('Authorization')

    # Log the JWT token
    if authorization_header and authorization_header.startswith('Bearer '):
        jwt_token = authorization_header.split('Bearer ')[1].strip()
        logging_utility.debug("JWT token: %s", jwt_token)
    else:
        jwt_token = None
        logging_utility.warning("Authorization header is missing or invalid")

    # Log the JWT identity
    current_user_id = get_jwt_identity()
    logging_utility.info("Current user ID: %s", current_user_id)

    data = request.get_json()
    if not data:
        logging_utility.warning("Missing JSON data in the request")
        return jsonify({"msg": "Missing JSON data"}), 400

    try:
        altitude = data['altitude']
        latitude = data['latitude']
        location_type = data['locationType']
        longitude = data['longitude']
        permission_status = data['permissionStatus']
    except KeyError as e:
        logging_utility.error("Invalid JSON data: %s", str(e))
        return jsonify({"msg": "Invalid JSON data"}), 400

    logging_utility.debug("Received location data: altitude=%s, latitude=%s, locationType=%s, longitude=%s, permissionStatus=%s",
                          altitude, latitude, location_type, longitude, permission_status)

    try:
        user_location = UserLocation(
            user_id=current_user_id,
            permission_status=permission_status,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude
        )
        db.session.add(user_location)
        db.session.commit()
        logging_utility.info("Location updated successfully for user %s", current_user_id)
        return jsonify({"msg": "Location updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging_utility.error("Error updating location: %s", str(e))
        return jsonify({"msg": f"Error updating location: {str(e)}"}), 500