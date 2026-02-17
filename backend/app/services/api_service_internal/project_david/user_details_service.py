from backend.app import create_app
from backend.app.models import FauxIdentity, User
# Create an instance of the LoggingUtility class
from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()


class UserDetailsService:
    def __init__(self):
        pass

    def get_user_details_by_faux_identity(self, faux_identity):

        app = create_app()

        with app.app_context():
            faux_identity_record = FauxIdentity.query.filter_by(
                faux_identity=faux_identity
            ).first()
            if faux_identity_record:
                real_user_id = faux_identity_record.user_id
                user = User.query.get(real_user_id)
                if user:
                    user_data = {
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.role,
                        "internal_role": user.internal_role,
                        # Add more user details as needed
                    }
                    logging_utility.info(
                        "User details retrieved successfully for faux identity: %s",
                        faux_identity,
                    )
                    return user_data
                else:
                    logging_utility.error(
                        "User not found for faux identity %s", faux_identity
                    )
                    return None
            else:
                logging_utility.error("Faux identity not found: %s", faux_identity)
                return None


if __name__ == "__main__":
    faux_identity = (
        "6bd0041a-0f68-439c-a054-9b735142982c"  # Replace with the desired faux identity
    )

    service = UserDetailsService()
    user_details = service.get_user_details_by_faux_identity(faux_identity)

    if user_details:
        print(f"User details for faux identity '{faux_identity}':")
        print(user_details)
    else:
        print(f"Failed to retrieve user details for faux identity '{faux_identity}'")
