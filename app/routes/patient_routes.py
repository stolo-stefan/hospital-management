from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Patient, Treatment, PatientAssistant, PatientTreatment
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import get_patient_by_id, get_current_user, check_json, get_user_by_id, check_role, update_user_fields

patients_bp = Blueprint("patients_bp", __name__)

@patients_bp.route('/register', methods=['POST'])
@jwt_required()
def create_patient():
    role_error = check_role(['General Manager', 'Doctor'])
    if role_error:
        return role_error

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if 'name' not in data or not data['name']:
        return jsonify({'error': 'Name field must be filled'}), 400

    if Patient.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Patient with this name already exists'}), 400

    new_patient = Patient(name=data['name'])
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({'message': 'Patient created successfully'}), 201

@patients_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_patients():
    patients = Patient.query.all()
    if not patients:
        return jsonify({'message':'No patients found'}),204
    return jsonify({'patients': [{'id': p.id, 'name': p.name} for p in patients]}), 200

@patients_bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    patient = get_patient_by_id(patient_id)
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    if isinstance(patient, dict):
        return patient
    return jsonify({'id': patient.id, 'name': patient.name}), 200

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    role_error = check_role(['General Manager', 'Doctor'])
    if role_error:
        return role_error

    patient = get_patient_by_id(patient_id)
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    if isinstance(patient, dict):
        return patient

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if 'name' in data and data['name']:
        if Patient.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Patient with this name already exists'}), 400
        patient.name = data['name']

    db.session.commit()
    return jsonify({'message': 'Patient updated successfully'}), 200

@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    role_error = check_role(['General Manager', 'Doctor'])
    if role_error:
        return role_error

    patient = Patient.query.get(patient_id)
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404

    from app.models.patient_assistant import PatientAssistant
    assistants_to_remove = PatientAssistant.query.filter_by(patient_id=patient.id).all()
    for pa_row in assistants_to_remove:
        db.session.delete(pa_row)

    db.session.delete(patient)
    db.session.commit()

    return jsonify({'message': 'Patient deleted successfully'}), 200

@patients_bp.route('/<int:patient_id>/assign', methods=['POST'])
@jwt_required()
def assign_patient_to_assistant(patient_id):
    current_user = get_current_user()
    if current_user['role'] not in ['General Manager', 'Doctor']:
        return jsonify({'error': 'Unauthorized'}), 401

    patient = get_patient_by_id(patient_id)
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    if isinstance(patient, dict):
        return patient

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if current_user['role'] == 'Doctor':
        doctor_id = current_user['id']
    else:
        if 'doctor_id' not in data or not data['doctor_id']:
            return jsonify({'error': 'doctor_id must be specified by the General Manager'}), 400
        doctor_id = data['doctor_id']

    existing_doctor = User.query.get(doctor_id)
    if not existing_doctor:
        return jsonify({'error': 'Doctor user not found'}), 404

    if 'assistant_id' not in data or not data['assistant_id']:
        return jsonify({'error': 'assistant_id is required'}), 400

    assistant_user = User.query.get(data['assistant_id'])
    if not assistant_user:
        return jsonify({'error': 'Assistant user not found'}), 404
    if assistant_user.role != 'Assistant':
        return jsonify({'error': 'User is not an Assistant'}), 400

    from app.models.patient_assistant import PatientAssistant

    existing_doctor_assignment = PatientAssistant.query.filter_by(patient_id=patient.id).first()
    if existing_doctor_assignment and existing_doctor_assignment.doctor_id != doctor_id:
        return jsonify({'error': 'This patient already belongs to another doctor'}), 409

    existing_relation = PatientAssistant.query.filter_by(
        patient_id=patient.id,
        assistant_id=assistant_user.id,
        doctor_id=doctor_id
    ).first()
    if existing_relation:
        return jsonify({'message': 'This patient is already assigned to that assistant under this doctor'}), 200

    new_assignment = PatientAssistant(
        patient_id=patient.id,
        assistant_id=assistant_user.id,
        doctor_id=doctor_id
    )
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({
        'message': f'Patient {patient_id} assigned to Assistant {assistant_user.id} under Doctor {doctor_id}'
    }), 201

@patients_bp.route('/doctor/patients', methods=['GET'])
@jwt_required()
def get_patients_by_doctor():
    current_user = get_current_user()
    if current_user['role'] not in ['Doctor', 'General Manager']:
        return jsonify({'error': 'Unauthorized'}), 401

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if current_user['role'] == 'Doctor':
        doctor_id = current_user['id']
    else:
        if 'doctor_id' not in data or not data['doctor_id']:
            return jsonify({'error': 'doctor_id must be specified by the General Manager'}), 400
        doctor_id = data['doctor_id']

    doctor = User.query.get(doctor_id)
    if not doctor or doctor.role != 'Doctor':
        return jsonify({'error': 'Doctor not found or invalid role'}), 404

    from app.models.patient_assistant import PatientAssistant

    assignments = (
        PatientAssistant.query
        .filter_by(doctor_id=doctor.id)
        .all()
    )
    if not assignments:
        return jsonify({'message': 'No patients found for this doctor'}), 200

    patient_ids = [a.patient_id for a in assignments]
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    result = [{'id': p.id, 'name': p.name} for p in patients]

    return jsonify({'doctor_id': doctor.id, 'patients': result}), 200