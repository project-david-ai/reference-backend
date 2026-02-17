from datetime import datetime

from flask_login import current_user, login_user
from werkzeug.security import check_password_hash

from backend.app.models import User
from backend.app.services.db_services.database_service import DatabaseService


class LoginService:

    def __init__(self, current_user, session):
        self.db_service = DatabaseService()
        self.session = session
        self.current_user = current_user
        self.user = None
        self.redirect_url = None
        print(
            f"LoginService initialized with current_user: {current_user} and session: {session}"
        )

    def _load_user_from_db(self, email):
        print(f"Attempting to load user with email: {email}")
        self.user = User.query.filter_by(email=email).first()
        if self.user:
            print(f"User loaded: {self.user}")
        else:
            print("No user found with that email.")

    def _authenticate_user(self, password):
        print(f"Authenticating user: {self.user.email if self.user else 'None'}")
        if self.user and check_password_hash(self.user.password_hash, password):
            print("Authentication successful.")
            return True
        else:
            print("Authentication failed.")
            return False

    def _set_last_login(self):
        if self.user:
            print(f"Setting last login for user: {self.user.email}")
            self.user.last_login = datetime.utcnow()
            self.db_service.update_user(self.user)
            print("Last login time updated.")
        else:
            print("No user to set last login for.")

    def process_request(self, request, form=None):
        # Assuming JSON data is sent from the frontend
        data = request.get_json()

        print(f"Processing login request for user: {data.get('email', 'None')}")
        if current_user.is_authenticated:
            print("User is already authenticated, redirecting to dashboard.")
            self.redirect_url = "http://127.0.0.1:3000/q-composer"
            return {"redirect_url": self.redirect_url}

        # Here, you would replace form validation with checking data presence
        if data:
            email = data.get("email")
            password = data.get("password")
            remember = data.get("remember", False)

            self._load_user_from_db(email)

            if not self._authenticate_user(password):
                # Consider using Flask's `flash` to send feedback messages to the frontend
                # flash("Invalid credentials", 'warning')
                self.redirect_url = None  # Or a specific error page
            elif not self.user.confirmed:
                # flash("Please confirm your email", 'warning')
                self.redirect_url = None
            elif not self.user.is_active:
                self.redirect_url = None  # Or a reactivation page
            else:
                login_user(self.user, remember=remember)
                self._set_last_login()
                self.redirect_url = "http://127.0.0.1:3000/q-composer"
        else:
            print("No data received.")

        result = {"redirect_url": self.redirect_url}
        print(f"Process request result: {result}")
        return result
