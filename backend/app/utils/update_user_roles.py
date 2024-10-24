import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from backend.app.extensions import db
from backend.app.models import User
from backend.app import create_app


def update_user_roles():
    try:
        # Create an application context
        app = create_app()
        with app.app_context():
            # Update all users with the default role of 'user'
            users = User.query.all()
            for user in users:
                user.role = 'user'
            db.session.commit()
            print("User roles updated successfully.")
    except Exception as e:
        print(f"An error occurred while updating user roles: {str(e)}")
        db.session.rollback()


if __name__ == "__main__":
    update_user_roles()