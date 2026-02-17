import os
from datetime import datetime

import sqlalchemy as sa
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from backend.app.extensions import db
from backend.app.services.identifier_service import IdentifierService
from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()


class LocalUser(UserMixin, db.Model):
    __tablename__ = "local_users"
    id = db.Column(
        db.String(255), primary_key=True, default=IdentifierService.generate_user_id()
    )
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    profile_settings = db.relationship(
        "ProfileSettings", backref="local_user", lazy=True, uselist=False
    )
    assistants = db.relationship("Assistant", backref="local_user", lazy=True)

    def __repr__(self):
        return f"<LocalUser {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ProfileSettings(db.Model):
    __tablename__ = "profile_settings"
    id = db.Column(
        db.String(255),
        primary_key=True,
        default=IdentifierService.generate_profile_id(),
    )
    user_id = db.Column(db.String(255), db.ForeignKey("local_users.id"), nullable=False)
    settings_data = db.Column(sa.JSON, nullable=True)

    def __repr__(self):
        return f"<ProfileSettings(user_id={self.user_id})>"


class Assistant(db.Model):
    __tablename__ = "assistants"
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("local_users.id"), nullable=False)
    assistant_id = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return (
            f"<Assistant(assistant_id={self.assistant_id}, "
            f"user_id={self.user_id}, type={self.type})>"
        )


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("local_users.id"), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)


class RevokedToken(db.Model):
    __tablename__ = "revoked_tokens"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"RevokedToken(jti='{self.jti}', revoked_at='{self.revoked_at}')"


def create_default_assistant(user_id: str) -> Assistant:
    """
    Upsert a default assistant using ENTITIES_ASSISTANT_ID from the environment.
    No upstream API calls are made.
    """
    env_assistant_id = os.getenv("ENTITIES_ASSISTANT_ID")
    if not env_assistant_id:
        raise RuntimeError("Missing ENTITIES_ASSISTANT_ID in environment")

    # Check if it already exists
    record = Assistant.query.filter_by(user_id=user_id, id=env_assistant_id).first()
    if record:
        logging_utility.info("Default assistant already exists for %s", user_id)
        return record

    # Create it locally
    logging_utility.info(
        "Creating local assistant record %s for user %s", env_assistant_id, user_id
    )
    new_record = Assistant(
        id=env_assistant_id,
        user_id=user_id,
        assistant_id=env_assistant_id,
        type="math_tutor",
    )
    db.session.add(new_record)
    db.session.commit()
    return new_record


def confirm_default_user() -> LocalUser:
    """
    Read ENTITIES_USER_ID from env and upsert a local admin user.
    """
    env_id = os.getenv("ENTITIES_USER_ID")
    if not env_id:
        raise RuntimeError("Missing ENTITIES_USER_ID in environment")

    local = LocalUser.query.filter_by(username="admin").first()
    if local:
        if local.id != env_id:
            logging_utility.info(
                "Updating local admin.id from %s → %s", local.id, env_id
            )
            local.id = env_id
            db.session.commit()
    else:
        logging_utility.info("Creating local admin user with ID %s", env_id)
        local = LocalUser(
            id=env_id,
            username="admin",
            first_name="Default",
            last_name="Admin",
            is_admin=True,
            role="admin",
        )
        local.set_password("admin")
        db.session.add(local)
        db.session.commit()

    return local


def initialize_database():
    """Create all tables, ensure default user & assistant exist."""
    db.create_all()
    admin = confirm_default_user()
    create_default_assistant(admin.id)
