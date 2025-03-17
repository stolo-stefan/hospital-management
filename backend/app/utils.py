from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash
from app.models import User, Patient, Treatment
from app import db

def get_current_user():
    # Retrieves the current logged-in user from the JWT token.
    # Returns the user identity (id, role) if authenticated.
    return get_jwt_identity()

def check_role(allowed_roles):
    # Checks if the current user has the required role(s).
    # If unauthorized, returns a 401 response.
    current_user = get_current_user()
    if current_user['role'] not in allowed_roles:
        return jsonify({'error': 'Unauthorized'}), 401
    return None

def check_json():
    #Validates if the request contains JSON data.
    if not request.is_json:
        return jsonify({'error': 'Invalid content - type must be application/json'}), 415
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    return data

def get_user_by_id(user_id):
    # Retrieves a user by their ID.
    return User.query.get(user_id)

def update_user_fields(user, data):
    # Updates user fields based on the provided JSON data.
    if 'name' in data and data['name']:
        user.name = data['name']
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    if 'role' in data and data['role']:
        user.role = data['role']
    db.session.commit()

def get_patient_by_id(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return None
    return patient

def get_treatment_by_id(treatment_id):
    #Retrieve a treatment by ID or return a 404 error.
    treatment = Treatment.query.get(treatment_id)
    if not treatment:
        return None
    return treatment
