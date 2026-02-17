from backend.app.services.api_service_internal.project_david.user_details_service import \
    UserDetailsService
from backend.app.services.logging_service.logger import LoggingUtility


class UserDetailsHandler:
    def __init__(self):

        self.user_details_service = UserDetailsService()

        self.logging_utility = LoggingUtility()

    def handle_get_user_details_by_faux_identity(self, arguments):
        self.logging_utility.info("Retrieving user details by faux identity")
        faux_identity = arguments.get("faux_identity", None)

        if faux_identity:
            user_details = self.user_details_service.get_user_details_by_faux_identity(
                faux_identity
            )

            if user_details:
                response = "User Details:\n\n"
                response += f"Username: {user_details.get('username', '')}\n"
                response += f"Email: {user_details.get('email', '')}\n"
                response += f"First Name: {user_details.get('first_name', '')}\n"
                response += f"Last Name: {user_details.get('last_name', '')}\n"
                response += f"Role: {user_details.get('role', '')}\n"
                response += f"Internal Role: {user_details.get('internal_role', '')}\n"
                response += f"Faux Identity: {user_details.get('faux_identity', '')}\n"
                response += "---\n"
            else:
                self.logging_utility.warning(
                    "Failed to retrieve user details for faux identity: %s",
                    faux_identity,
                )
                response = f"Failed to retrieve user details for faux identity: {faux_identity}"
        else:
            self.logging_utility.warning("Faux identity not provided")
            response = "Faux identity not provided."

        return response
