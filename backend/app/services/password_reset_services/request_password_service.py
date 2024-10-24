from datetime import datetime, timedelta
from backend.app.services.indentity_services.pin_service import PinService
from backend.app.services.email_services.email_service import EmailService
from backend.app.models import User, PasswordResetToken
from backend.app.extensions import db
from backend.app.services.message_services.messages import PASSWORD_RESET_REQUEST, EMAIL_NOT_FOUND
from backend.app.services.twillo_services.twillo_service import send_sms


class ResetPasswordService:
    def __init__(self):
        self.email_service = EmailService()
        self.user = None

    def get_user_by_email(self, email):
        print(f"Attempting to fetch user with email: {email}")
        self.user = User.query.filter_by(email=email).first()
        if self.user:
            print(f"Successfully fetched user with email: {email}")
        else:
            print(f"No user found with email: {email}")

    def create_reset_pin_for_user(self):
        try:
            pin = PinService.generate_pin()
            print(pin)
            self.user.password_reset_pin = pin
            self.user.password_reset_expires_at = datetime.utcnow() + timedelta(seconds=1800)
            db.session.commit()

            # Create a password reset token entry in the database
            expiration_date = datetime.utcnow() + timedelta(seconds=1800)
            password_reset_token = PasswordResetToken(user_id=self.user.id, token=pin, expiration_date=expiration_date)
            db.session.add(password_reset_token)
            db.session.commit()

            print("Updated user with reset PIN and expiry.")

            # Send the password reset email
            reset_url = 'http://example.com/reset-password'  # Replace with your actual reset URL
            self.email_service.send_password_reset_email(self.user.email, self.user.username, self.user.password_reset_pin, reset_url)
        except Exception as e:
            print(f"An error occurred while creating reset PIN for user: {e}")

    def send_password_reset_sms(self):
        try:
            mobile_number = self.user.mobile_number
            message = f"Your password reset PIN is: {self.user.password_reset_pin}"
            send_sms(mobile_number, message)
        except Exception as e:
            print(f"An error occurred while sending password reset SMS: {e}")

    def resend_pin(self, email):
        self.get_user_by_email(email)
        if self.user:
            self.create_reset_pin_for_user()
            print("Resent PIN successfully.")
            return {"status": "success", "message": "PIN resent successfully"}
        else:
            print(f"Failed to resend PIN for email: {email}")
            return {"status": "warning", "message": EMAIL_NOT_FOUND}

    def process_request(self, email):
        self.get_user_by_email(email)
        if self.user:
            self.create_reset_pin_for_user()
            self.send_password_reset_sms()
            print("Processed password reset request successfully.")
            return {"status": "success", "message": PASSWORD_RESET_REQUEST}
        else:
            print(f"Password reset request failed for email: {email}")
            return {"status": "warning", "message": EMAIL_NOT_FOUND}