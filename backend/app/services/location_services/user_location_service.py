# backend/app/services/user_location_service.py
from backend.app.models import User, UserLocation
from backend.app.extensions import db
from datetime import datetime
from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()


class UserLocationService:
    @staticmethod
    def capture_user_location(user_id, permission_status, location_type, latitude, longitude, altitude):
        logging_utility.info(
            "Capturing location for user_id=%s with permission_status=%s, location_type=%s, latitude=%s, longitude=%s",
            user_id, permission_status, location_type, latitude, longitude
        )

        user = User.query.get(user_id)
        if not user:
            logging_utility.error("User not found for user_id=%s", user_id)
            raise ValueError("User not found")

        try:
            location = UserLocation(
                user_id=user_id,
                permission_status=permission_status,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                timestamp=datetime.utcnow()
            )
            db.session.add(location)
            db.session.commit()
            logging_utility.info("Location captured and committed to the database for user_id=%s", user_id)

            return location
        except Exception as e:
            logging_utility.error("An error occurred while capturing location for user_id=%s: %s", user_id, str(e))
            db.session.rollback()
            raise
