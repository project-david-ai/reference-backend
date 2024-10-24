# run.py
from backend.app import create_app
from backend.app.models import initialize_database
from backend.app.services.logging_service.logger import LoggingUtility

app = create_app()

# Configure logging
logging_utility = LoggingUtility(app)
app.logger.addHandler(logging_utility.handler)
app.logger.setLevel(logging_utility.level)


def create_tables():
    with app.app_context():
        initialize_database()

# Uncomment if you want to create tables when the app runs.
# But be careful in production!
create_tables()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
