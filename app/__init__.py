from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from config import config
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    env = os.getenv("FLASK_ENV", "development")  # Detect environment (default: development)
    print(f"DEBUG: FLASK_ENV = '{env}'")
    app = Flask(__name__)
    app.config.from_object(config[env])  # Load the correct config

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.routes.auth_routes import auth_bp
    from app.routes.manager_routes import manager_bp
    from app.routes.doctor_routes import doctor_bp
    from app.routes.assistant_routes import assistant_bp
    from app.routes.report_routes import report_bp
    from app.routes.patient_routes import patients_bp
    from app.routes.treatment_routes import treatments_bp

    SWAGGER_URL = "/api/docs"
    API_URL = "/static/swagger.yaml"

    swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(manager_bp, url_prefix='/api/managers')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctors')
    app.register_blueprint(assistant_bp, url_prefix='/api/assistants')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(patients_bp, url_prefix="/api/patients")
    app.register_blueprint(treatments_bp, url_prefix="/api/treatments")

    return app