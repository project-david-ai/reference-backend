import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from backend.app.extensions import db
from backend.app.models import User, FauxIdentity
from backend.app import create_app
from backend.app.utils.generate_uid import generate_uuid


def assign_faux_identities():
    try:
        # Create an application context
        app = create_app()
        with app.app_context():
            users = User.query.all()
            for user in users:
                if not user.faux_identity:
                    faux_identity = FauxIdentity(
                        user_id=user.id,
                        faux_identity=generate_uuid()
                    )
                    db.session.add(faux_identity)
            db.session.commit()
            print("Faux identities assigned successfully to all users.")
    except Exception as e:
        print(f"An error occurred while assigning faux identities: {str(e)}")
        db.session.rollback()


if __name__ == "__main__":
    assign_faux_identities()