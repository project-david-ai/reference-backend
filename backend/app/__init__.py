import json
import os

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate

from backend.app.extensions import JWTManager, db
from backend.app.services.logging_service.logger import LoggingUtility
# Removed: from backend.app.utils.tools import str_to_bool
from config import config

from dotenv import load_dotenv

login_manager = LoginManager()

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

load_dotenv()

def create_app(config_name='default'):
    app = Flask(__name__)
    logging_utility = LoggingUtility(app)
    configure_app(app, config_name)
    login_manager.init_app(app)
    jwt = JWTManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        pass
        # user_db_service = UserDatabaseService()
        # return user_db_service.get_user_by_id(str(user_id))

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)
    migrate = Migrate(app, db)
    register_blueprints(app)
    register_template_filters(app)
    print("Navigate to Q login: http://127.0.0.1:5000/bp_auth/login /")
    return app

def configure_app(app, config_name):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    app.debug = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')
    app.config.from_object(config[config_name])

def register_blueprints(app):
    from backend.app.bp_auth import bp_auth as bp_auth_blueprint
    from backend.app.bp_identity import bp_identity as bp_identity_blueprint
    from backend.app.bp_common import bp_common as bp_common_blueprint
    from backend.app.bp_llama import bp_llama as bp_llama_blueprint
    from backend.app.bp_service_drones import bp_service_drones as bp_service_drones_blueprint
    from backend.app.bp_legal import bp_legal as bp_legal_blueprint
    from backend.app.bp_account import bp_account as bp_account_blueprint
    from backend.app.bp_files import bp_files as bp_files_blueprint
    from backend.app.bp_speech import bp_speech as bp_speech_blueprint
    from backend.app.bp_location import bp_location as bp_location_blueprint

    app.register_blueprint(bp_files_blueprint, url_prefix='/bp_files')
    app.register_blueprint(bp_auth_blueprint, url_prefix='/bp_auth')
    app.register_blueprint(bp_legal_blueprint, url_prefix='/bp_legal')
    app.register_blueprint(bp_account_blueprint, url_prefix='/bp_account')
    app.register_blueprint(bp_common_blueprint, url_prefix='/bp_common')
    app.register_blueprint(bp_identity_blueprint, url_prefix='/bp_identity')
    app.register_blueprint(bp_llama_blueprint, url_prefix='/bp_llama')
    app.register_blueprint(bp_service_drones_blueprint, url_prefix='/bp_service_drones')
    app.register_blueprint(bp_speech_blueprint, url_prefix='/bp_speech')
    app.register_blueprint(bp_location_blueprint, url_prefix='/bp_location')

def register_template_filters(app):
    @app.template_filter('json_loads')
    def json_loads(value):
        return json.loads(value)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
