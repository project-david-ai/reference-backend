from backend.app import create_app, db
from backend.app.models import FauxIdentity, User, UserLocation
from backend.app.services.logging_service.logger import LoggingUtility

# Create an instance of the LoggingUtility class
logging_utility = LoggingUtility()


class UserLocationService:
    def __init__(self):
        pass

    def get_user_locations(self, faux_identity, limit=None):
        app = create_app()

        with app.app_context():
            faux_identity_record = FauxIdentity.query.filter_by(
                faux_identity=faux_identity
            ).first()
            if faux_identity_record:
                real_user_id = faux_identity_record.user_id
                with db.session.no_autoflush:
                    user = db.session.get(User, real_user_id)
                if user:
                    query = UserLocation.query.filter_by(user_id=real_user_id).order_by(
                        UserLocation.timestamp.desc()
                    )
                    if limit:
                        query = query.limit(limit)
                    user_locations = [
                        {
                            "id": location.id,
                            "permission_status": location.permission_status,
                            "location_type": location.location_type,
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "timestamp": location.timestamp.isoformat(),
                        }
                        for location in query.all()
                    ]
                    if user_locations:
                        logging_utility.info(
                            "User locations retrieved successfully for faux identity: %s",
                            faux_identity,
                        )
                        return user_locations
                    else:
                        logging_utility.error(
                            "No location found for user with faux identity %s",
                            faux_identity,
                        )
                        return []
                else:
                    logging_utility.error(
                        "User not found for faux identity %s", faux_identity
                    )
                    return []
            else:
                logging_utility.error("Faux identity not found: %s", faux_identity)
                return []


if __name__ == "__main__":
    faux_identity = (
        "6bd0041a-0f68-439c-a054-9b735142982c"  # Replace with the desired faux identity
    )
    limit = 3  # Limit the number of user locations to retrieve

    service = UserLocationService()
    user_locations = service.get_user_locations(faux_identity, limit)

    if user_locations:
        print(f"User locations (up to {limit}) for faux identity '{faux_identity}':")
        for location in user_locations:
            print(location)
    else:
        print(f"Failed to retrieve user locations for faux identity '{faux_identity}'")
