# backend/app/bp_account/routes.py
import time

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.services.logging_service.logger import LoggingUtility
from . import bp_account

# Initialize the logging utility
logging_utility = LoggingUtility()


@bp_account.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    logging_utility.info("Entering delete_account")
    try:
        user_id = get_jwt_identity()
        if not user_id:
            logging_utility.warning("User ID is missing from the JWT.")
            return jsonify({'error': 'User ID is missing from the JWT.'}), 400

        db_service = UserAllowedDatabaseService()
        logging_utility.info("Deleting account for user ID: %s", user_id)
        success = db_service.delete_user_account(user_id)

        if success:
            logging_utility.info("Account deleted successfully for user ID: %s", user_id)
            return jsonify({'message': 'Account deleted successfully.'}), 200
        else:
            logging_utility.error("An error occurred while deleting the account for user ID: %s", user_id)
            return jsonify({'error': 'An error occurred while deleting the account.'}), 500
    except Exception as e:
        logging_utility.exception("An error occurred: %s", str(e))
        return jsonify({'error': 'An unexpected error occurred while deleting the account.'}), 500