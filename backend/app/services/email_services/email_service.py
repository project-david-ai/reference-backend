import os

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()


class EmailService:
    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("EMAIL_SENDER")

    def send_password_reset_email(self, email, username, reset_pin, reset_url):
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject="Reset Your Password",
                html_content=f'<p>Dear {username},</p><p>Your password reset PIN is: {reset_pin}</p><p>Please click the following link to reset your password: <a href="{reset_url}">{reset_url}</a></p>',
            )

            sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
            response = sendgrid_client.send(message)

            print(
                f"Password reset email sent to {email}. Status code: {response.status_code}"
            )
        except Exception as e:
            print(f"Error sending password reset email to {email}: {e}")

    def send_gen_user_email(self, email, title, message_body):
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject=title,
                html_content=message_body,
            )

            sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
            response = sendgrid_client.send(message)

            print(
                f"General user email sent to {email}. Status code: {response.status_code}"
            )
        except Exception as e:
            print(f"Error sending general user email to {email}: {e}")

    def send_sentinel_drone_summary(self, email, summary):
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject="Sentinel Drone Summary",
                html_content=f"""
                <html>
                    <body>
                        <h2>Sentinel Drone Summary</h2>
                        <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;">{summary}</pre>
                    </body>
                </html>
                """,
            )

            sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
            response = sendgrid_client.send(message)

            print(
                f"Sentinel drone summary email sent to {email}. Status code: {response.status_code}"
            )
        except Exception as e:
            print(f"Error sending sentinel drone summary email to {email}: {e}")
