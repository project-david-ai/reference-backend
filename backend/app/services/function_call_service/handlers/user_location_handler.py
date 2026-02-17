from backend.app.services.api_service_internal.project_david.user_location_service import \
    UserLocationService
from backend.app.services.logging_service.logger import LoggingUtility


class UserLocationHandler:
    def __init__(self):
        self.user_location_service = UserLocationService()
        self.logging_utility = LoggingUtility()

    def handle_get_user_locations(self, arguments):
        self.logging_utility.info("Retrieving user locations by faux identity")
        faux_identity = arguments.get("faux_identity", None)
        limit = arguments.get("limit", None)

        if faux_identity:
            user_locations = self.user_location_service.get_user_locations(
                faux_identity, limit
            )

            if user_locations:
                response = "User Locations:\n\n"
                for location in user_locations:
                    response += f"ID: {location.get('id', '')}\n"
                    response += (
                        f"Permission Status: {location.get('permission_status', '')}\n"
                    )
                    response += f"Location Type: {location.get('location_type', '')}\n"
                    response += f"Latitude: {location.get('latitude', '')}\n"
                    response += f"Longitude: {location.get('longitude', '')}\n"
                    response += f"Timestamp: {location.get('timestamp', '')}\n"
                    response += "---\n"
            else:
                self.logging_utility.warning(
                    "Failed to retrieve user locations for faux identity: %s",
                    faux_identity,
                )
                response = f"Failed to retrieve user locations for faux identity: {faux_identity}"
        else:
            self.logging_utility.warning("Faux identity not provided")
            response = "Faux identity not provided."

        return response
