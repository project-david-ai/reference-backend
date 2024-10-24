import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from backend.app.extensions import db
from backend.app.models import User
from backend.app import create_app


def update_user_role_by_email(email, new_role):
    try:
        # Create an application context
        app = create_app()
        with app.app_context():
            # Find the user by their email
            user = User.query.filter_by(email=email).first()
            if user:
                # Update the user's role
                user.role = new_role
                db.session.commit()
                print(f"User role updated successfully for user with email: {email}")
            else:
                print(f"User with email {email} not found.")
    except Exception as e:
        print(f"An error occurred while updating the user role: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    # Example usage: update_user_role_by_email('user@example.com', 'admin')
    update_user_role_by_email('prime.thanos336@gmail.com', 'developer')