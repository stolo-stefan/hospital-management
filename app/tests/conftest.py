import pytest
from sqlalchemy import text
from app import create_app, db
from app.models import User, Patient, Treatment, PatientAssistant, PatientTreatment
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
import os

@pytest.fixture
def app():
    """Create a separate test app instance using MySQL test database."""
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("TEST_DATABASE_URI")

    with app.app_context():
        db.create_all()
        yield app 
        db.session.remove()
        db.drop_all()

        with db.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user in the database"""
    user = User(name="testuser", password_hash=generate_password_hash("testpassword"), role="General Manager")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def general_manager(app):
    """Create a General Manager user and return session-bound instance"""
    with app.app_context():
        manager = User(name="manager", password_hash=generate_password_hash("password"), role="General Manager")
        db.session.add(manager)
        db.session.commit()
        return User.query.get(manager.id) 

@pytest.fixture
def auth_headers_manager(app, general_manager):
    """Generate a valid JWT token for authentication"""
    with app.app_context():
        token = create_access_token(identity={"id": general_manager.id, "role": general_manager.role})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def doctor(app):
    """Create a Doctor user and return a fresh session-bound instance"""
    with app.app_context():
        doctor = User(name="doctor1", password_hash=generate_password_hash("password"), role="Doctor")
        db.session.add(doctor)
        db.session.commit()
        return User.query.get(doctor.id)
    
@pytest.fixture
def auth_headers_doctor(app, doctor):
    """Generate a valid JWT token for authentication"""
    with app.app_context():
        token = create_access_token(identity={"id": doctor.id, "role": doctor.role})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def assistant(app):
    """Create an Assistant user and return a fresh session-bound instance"""
    with app.app_context():
        assistant = User(name="assistant1", password_hash=generate_password_hash("password"), role="Assistant")
        db.session.add(assistant)
        db.session.commit()
        return User.query.get(assistant.id)
    
@pytest.fixture
def auth_headers_assistant(app, assistant):
    """Generate a valid JWT token for authentication"""
    with app.app_context():
        token = create_access_token(identity={"id": assistant.id, "role": assistant.role})
    return {"Authorization": f"Bearer {token}"}
    
@pytest.fixture
def patient(app):
    """Create a Patient user and return a fresh session-bound instance"""
    with app.app_context():
        patient = Patient(name="patient1")
        db.session.add(patient)
        db.session.commit()
        return Patient.query.get(patient.id)

@pytest.fixture
def unauthorized_headers():
    """Return an empty Authorization header for unauthorized access tests"""
    return {"Authorization": ""}

@pytest.fixture
def doctor_assistant_patient_association(app, doctor, assistant, patient):
    """Create an entry in PatientAssistant table"""
    with app.app_context():
        patient_assistant = PatientAssistant(
            patient_id=patient.id,
            assistant_id=assistant.id,
            doctor_id=doctor.id 
        )
        db.session.add(patient_assistant)
        db.session.commit()

        return PatientAssistant.query.filter_by(
            patient_id=patient.id,
            doctor_id=doctor.id
        ).first()

@pytest.fixture
def treatment(app):
    """Create a Treatment and return a session-bound instance"""
    with app.app_context():
        treatment = Treatment(name="Physical Therapy", description="A therapy session for injury recovery.")
        db.session.add(treatment)
        db.session.commit()
        return Treatment.query.get(treatment.id)

@pytest.fixture
def patient_treatment_assosciation(app, doctor, assistant, patient, treatment):
    """Create an entry in the patient treatment table"""
    with app.app_context():
        patient_treatment = PatientTreatment(
            patient_id=patient.id,
            treatment_id=treatment.id,
            prescribed_by=doctor.id 
        )
        db.session.add(patient_treatment)
        db.session.commit()

        return PatientTreatment.query.filter_by(
            patient_id=patient.id,
            treatment_id=treatment.id
        ).first()
