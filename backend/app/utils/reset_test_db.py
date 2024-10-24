from backend.app import create_app
from backend.app.extensions import db
from backend.app.models import LocalUser

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    print("Dropped all tables")

    # Create all tables
    db.create_all()
    print("Created all tables")

    # Initialize with default data
    LocalUser.create_default_user()
    print("Inserted default user")
