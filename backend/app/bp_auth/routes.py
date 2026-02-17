# backend/app/bp_auth/routes.py
import os
from datetime import timedelta

from flask import jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt, get_jwt_identity,
                                jwt_required)
from werkzeug.security import check_password_hash

from backend.app.extensions import db
from backend.app.models import LocalUser, RevokedToken
from backend.app.services.logging_service.logger import LoggingUtility

from . import bp_auth

logging_utility = LoggingUtility()


@bp_auth.route("api/login", methods=["POST"])
def login():
    logging_utility.info("Entering login")

    # Get the username and password from the request
    username = request.json.get("username")
    password = request.json.get("password")

    logging_utility.info("Login attempt for username: %s", username)

    # Find the user in the database
    user = LocalUser.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        logging_utility.info("Successful login for user ID: %s", user.id)

        # Create an access token with a longer expiration time (e.g., 90 days)
        access_token = create_access_token(
            identity=str(user.id), expires_delta=timedelta(days=90)
        )

        # Prepare the user information to be included in the response
        user_info = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            # Include any other relevant user fields
        }

        logging_utility.info("User information for successful login: %s", user_info)

        # Return the access token and user information in the response
        return jsonify(access_token=access_token, user=user_info), 200
    else:
        logging_utility.warning("Invalid login attempt for username: %s", username)
        return jsonify({"message": "Invalid credentials"}), 401


@bp_auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    logging_utility.info("Entering logout")

    try:
        jwt = get_jwt()
        jti = jwt["jti"]

        logging_utility.info("Revoking token with JTI: %s", jti)

        # Add the JTI to the RevokedToken table
        revoked_token = RevokedToken(jti=jti)
        db.session.add(revoked_token)
        db.session.commit()

        logging_utility.info("Token revoked successfully")

        return jsonify({"message": "Logout successful"}), 200

    except Exception as e:
        logging_utility.error("Error occurred during logout: %s", str(e))
        db.session.rollback()
        return jsonify({"error": "An error occurred during logout"}), 500


@bp_auth.route("/refresh_token", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    logging_utility.info("Entering refresh_token")

    try:
        # Get the user ID from the refresh token
        user_id = get_jwt_identity()

        logging_utility.info("Refreshing token for user ID: %s", user_id)

        # Generate a new access token
        new_access_token = create_access_token(identity=user_id)

        logging_utility.info("New access token generated for user ID: %s", user_id)

        return jsonify(access_token=new_access_token), 200

    except Exception as e:
        logging_utility.error("Error occurred during token refresh: %s", str(e))
        return jsonify({"error": "An error occurred during token refresh"}), 500


@bp_auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    logging_utility.info("Entering protected route")

    try:
        # Access the identity of the current user with get_jwt_identity
        current_user_id = get_jwt_identity()

        logging_utility.info(
            "Retrieving user information for user ID: %s", current_user_id
        )

        # Retrieve the user information from the database based on the user ID
        user = LocalUser.query.get(current_user_id)

        if user:
            logging_utility.info("User found with ID: %s", user.id)

            # Prepare the user information to be returned
            user_info = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                # Include any other relevant user fields
            }

            logging_utility.info("User information: %s", user_info)

            return jsonify(user=user_info), 200
        else:
            logging_utility.warning("User not found with ID: %s", current_user_id)
            return jsonify({"message": "User not found"}), 404

    except Exception as e:
        logging_utility.error("Error occurred in protected route: %s", str(e))
        return jsonify({"error": "An error occurred"}), 500
