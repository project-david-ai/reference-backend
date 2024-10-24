from datetime import datetime
import sqlalchemy as sa
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import entities_api
from backend.app.extensions import db
from backend.app.services.identifier_service import IdentifierService
from backend.app.services.logging_service.logger import LoggingUtility

# Initialize the client
client = entities_api.OllamaClient()

logging_utility = LoggingUtility()


class LocalUser(UserMixin, db.Model):
    __tablename__ = 'local_users'
    id = db.Column(db.String(255), primary_key=True, default=IdentifierService.generate_user_id())
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    # Relationship to ProfileSettings
    profile_settings = db.relationship('ProfileSettings', backref='local_user', lazy=True, uselist=False)

    # Relationship to Assistants
    assistants = db.relationship('Assistant', backref='local_user', lazy=True)

    def __repr__(self):
        return f'<LocalUser {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_default_user():
        """Creates a default admin user if no users exist."""
        if not LocalUser.query.first():
            default_user = LocalUser(
                username='admin',
                first_name='Default',
                last_name='Admin',
                is_admin=True,
                role='admin'
            )
            default_user.set_password('admin')
            db.session.add(default_user)
            db.session.commit()


class ProfileSettings(db.Model):
    __tablename__ = 'profile_settings'
    id = db.Column(db.String(255), primary_key=True, default=IdentifierService.generate_profile_id())
    user_id = db.Column(db.String(255), db.ForeignKey('local_users.id'), nullable=False)
    settings_data = db.Column(sa.JSON, nullable=True)

    def __repr__(self):
        return f'<ProfileSettings(user_id={self.user_id})>'


class Assistant(db.Model):
    __tablename__ = 'assistants'
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('local_users.id'), nullable=False)
    assistant_id = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Assistant(assistant_id={self.assistant_id}, user_id={self.user_id}, type={self.type})>'


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('local_users.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"RevokedToken(jti='{self.jti}', revoked_at='{self.revoked_at}')"


def create_default_assistant(user_id):
    try:
        assistant_record = Assistant.query.filter_by(user_id=user_id).first()
        if not assistant_record:
            assistant = client.assistant_service.create_assistant(
                name='Mathy',
                user_id=user_id,
                description='My helpful maths tutor',
                model='llama3.1',
                instructions='Be as kind, intelligent, and helpful',

            )
            assistant_id = assistant.id
            assistant_type = "math_tutor"  # Replace with the appropriate type for your assistant

            logging_utility.info("Created default assistant: %s with assistant ID: %s", assistant, assistant_id)

            new_assistant_record = Assistant(id=assistant_id, user_id=user_id, assistant_id=assistant_id, type=assistant_type)
            db.session.add(new_assistant_record)
            db.session.commit()
            return new_assistant_record
        else:
            logging_utility.info("Default assistant already exists for user ID: %s", user_id)
            return assistant_record
    except Exception as e:
        logging_utility.error("Error in create_default_assistant: %s", str(e))
        db.session.rollback()
        raise


def confirm_user_exists_or_create(user_id):
    try:
        user = client.user_service.retrieve_user(user_id=user_id)
        logging_utility.info("User exists in the upstream API: %s", user)
        return user
    except Exception as e:
        logging_utility.warning("User not found in the upstream API, creating a new user: %s", str(e))
        new_user = client.user_service.create_user(
            username='admin',
            first_name='Default',
            last_name='Admin',
            password='admin'
        )
        logging_utility.info("Created new user in the upstream API: %s", new_user)

        # Update the local database with the new user ID
        default_user = LocalUser.query.filter_by(username='admin').first()
        if default_user:
            default_user.id = new_user.id
        else:
            default_user = LocalUser(
                id=new_user.id,
                username='admin',
                first_name='Default',
                last_name='Admin',
                password_hash=generate_password_hash('admin'),
                is_admin=True,
                role='admin'
            )
            db.session.add(default_user)
        db.session.commit()
        logging_utility.info("Updated local database with new user ID: %s", new_user.id)

        return new_user


def confirm_default_user():
    default_user = LocalUser.query.filter_by(username='admin').first()

    if not default_user:
        # No default user exists locally, create one
        try:
            new_user = client.user_service.create_user(
                username='admin',
                first_name='Default',
                last_name='Admin',
                password='admin'
            )
            logging_utility.info("Created new user in the upstream API: %s", new_user)
            default_user = LocalUser(
                id=new_user.id,
                username='admin',
                first_name='Default',
                last_name='Admin',
                password_hash=generate_password_hash('admin'),
                is_admin=True,
                role='admin'
            )
            db.session.add(default_user)
            db.session.commit()
        except Exception as e:
            logging_utility.error("Error creating user in the upstream API: %s", str(e))
            raise

    else:
        try:
            # Check if the user exists in the upstream API
            confirmed_user = client.user_service.retrieve_user(user_id=default_user.id)
            logging_utility.info("User exists in the upstream API: %s", confirmed_user)
        except Exception as e:
            logging_utility.warning("User ID %s not found in the upstream API: %s", default_user.id, str(e))
            try:
                # Drop the current ID and create a new user in the API
                new_user = client.user_service.create_user(
                    name='admin',
                )
                logging_utility.info("Created new user in the upstream API: %s", new_user)

                # Update the local record with the new ID
                default_user.id = new_user.id
                db.session.commit()
                logging_utility.info("Updated local database with new user ID: %s", new_user.id)
            except Exception as inner_e:
                logging_utility.error("Error creating new user in the upstream API after dropping ID: %s", str(inner_e))
                raise

    return default_user


def initialize_database():
    db.create_all()
    confirmed_user = confirm_default_user()
    create_default_assistant(confirmed_user.id)
