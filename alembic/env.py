from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Ensure that the application's package is on the path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the application's create_app function and models
from backend.app import create_app
from backend.app.extensions import db

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Set up the Flask app and get the SQLALCHEMY_DATABASE_URI from the Flask config
flask_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
database_url = flask_app.config['SQLALCHEMY_DATABASE_URI']
config.set_main_option('sqlalchemy.url', database_url)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL and not an Engine, though an Engine is acceptable here as well.
    By skipping the Engine creation we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
