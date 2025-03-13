import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import Treatment, Patient, PatientTreatment, PatientAssistant, TreatmentLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import get_current_user, check_json, check_role, get_treatment_by_id, get_patient_by_id

treatments_bp = Blueprint("treatments_bp", __name__)

@treatments_bp.route('/register', methods=['POST'])
@jwt_required()
def create_treatment():
    role_error = check_role(['General Manager', 'Doctor'])
    if role_error:
        return role_error

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if 'name' not in data or not data['name']:
        return jsonify({'error': 'Name field must be filled'}), 400

    if 'description' not in data or not data['description']:
        return jsonify({'error': 'Description field must be filled'}), 400

    if Treatment.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Treatment with this name already exists'}), 400

    new_treatment = Treatment(name=data['name'], description=data['description'])
    db.session.add(new_treatment)
    db.session.commit()

    return jsonify({'message': 'Treatment created successfully'}), 201


@treatments_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_treatments():
    treatments = Treatment.query.all()
    if not treatments:
        return jsonify({'message':'No treatments found'}), 204
    return jsonify({'treatments': [{'id': t.id, 'name': t.name, 'description': t.description} for t in treatments]}), 200

@treatments_bp.route('/<int:treatment_id>', methods=['GET'])
@jwt_required()
def get_treatment(treatment_id):
    treatment = get_treatment_by_id(treatment_id)
    if treatment is None:
        return jsonify({'error': 'Treatment not found'}), 404
    if isinstance(treatment, dict):
        return treatment
    return jsonify({'id': treatment.id, 'name': treatment.name, 'description': treatment.description}), 200

@treatments_bp.route('/<int:treatment_id>', methods=['PUT'])
@jwt_required()
def update_treatment(treatment_id):
    role_error = check_role(['General Manager', 'Doctor'])
    if role_error:
        return role_error

    treatment = get_treatment_by_id(treatment_id)
    if treatment is None:
        return jsonify({'error': 'Treatment not found'}), 404
    if isinstance(treatment, dict):
        return treatment

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if 'name' in data and data['name']:
        if Treatment.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Treatment with this name already exists'}), 400
        treatment.name = data['name']

    if 'description' in data and data['description']:
        treatment.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Treatment updated successfully'}), 200

@treatments_bp.route('/<int:treatment_id>', methods=['DELETE'])
@jwt_required()
def delete_treatment(treatment_id):
    role_error = check_role(['General Manager', 'Doctor'])
    if role_error:
        return role_error

    treatment = get_treatment_by_id(treatment_id)
    if treatment is None:
        return jsonify({'error': 'Treatment not found'}), 404
    if isinstance(treatment, dict):
        return treatment 

    patient_treatments_to_delete = PatientTreatment.query.filter_by(treatment_id=treatment.id).all()
    for pt in patient_treatments_to_delete:
        db.session.delete(pt)

    db.session.commit()

    db.session.delete(treatment)
    db.session.commit()

    return jsonify({'message': 'Treatment deleted successfully'}), 200

@treatments_bp.route('/<int:treatment_id>/prescribe/<int:patient_id>', methods=['POST'])
@jwt_required()
def prescribe_treatment_to_patient(treatment_id, patient_id):
    """
    [POST] Assigns an existing Treatment to a Patient. The doctor must already
    supervise this patient (i.e., patient_assistants table must link them).
    Only that supervising Doctor can prescribe.
    Body (optional):
      - 'status' -> 'prescribed' (default) or 'applied' (not typical here)
    Returns JSON with success message or error.
    """

    current_user = get_current_user()
    if current_user['role'] != 'Doctor':
        return jsonify({'error': 'Only a Doctor can prescribe treatments'}), 401
    patient = get_patient_by_id(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    supervising_relationship = PatientAssistant.query.filter_by(
        patient_id=patient_id,
        doctor_id=current_user['id']
    ).first()
    if not supervising_relationship:
        return jsonify({'error': 'This doctor does not supervise the patient'}), 403

    treatment = get_treatment(treatment_id)
    if not treatment:
        return jsonify({'error': 'Treatment not found'}), 404

    existing_treatment = PatientTreatment.query.filter_by(
        patient_id=patient.id,
        treatment_id=treatment_id
    ).first()

    if existing_treatment:
        return jsonify({'message': 'This treatment has already been prescribed to the patient'}), 200

    new_patient_treatment = PatientTreatment(
        patient_id=patient.id,
        treatment_id=treatment_id,
        prescribed_by=current_user['id'],
        prescribed_at=datetime.datetime.now(),
    )
    db.session.add(new_patient_treatment)
    db.session.commit()

    return jsonify({
        'message': f'Treatment {treatment_id} prescribed to Patient {patient_id} by Doctor {current_user["id"]}',
        'status': new_patient_treatment.status
    }), 201

@treatments_bp.route('/<int:treatment_id>/apply/<int:patient_id>', methods=['POST'])
@jwt_required()
def apply_treatment(patient_id, treatment_id):
    """
    [POST] Marks a prescribed treatment as applied by an Assistant.
    - The Assistant must be assigned to the Patient.
    - The Treatment must be in "prescribed" status before it can be applied.
    - Assistant ID is taken from the JWT.
    - Patient ID and Treatment ID are in the URL.
    Returns JSON with success message or error.
    """

    current_user = get_current_user()
    if current_user['role'] != 'Assistant':
        return jsonify({'error': 'Only an Assistant can apply treatments'}), 403
    assistant_id = current_user['id']
    
    patient = get_patient_by_id(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    assistant_assignment = PatientAssistant.query.filter_by(
        patient_id=patient_id,
        assistant_id=assistant_id
    ).first()
    if not assistant_assignment:
        return jsonify({'error': 'This Assistant is not assigned to the patient'}), 403

    treatment = Treatment.query.get(treatment_id)
    if not treatment:
        return jsonify({'error': 'Treatment not found'}), 404

    patient_treatment = PatientTreatment.query.filter_by(
        patient_id=patient_id,
        treatment_id=treatment_id
    ).first()
    if not patient_treatment:
        return jsonify({'error': 'Treatment is not prescribed to this patient'}), 404

    if patient_treatment.status != 'prescribed':
        return jsonify({'error': 'This treatment has already been applied'}), 400

    patient_treatment.applied_by = assistant_id
    patient_treatment.applied_at = datetime.datetime.now()
    patient_treatment.status = 'applied'

    db.session.commit()

    new_log = TreatmentLog(patient_id = patient_id, treatment_id = treatment_id, applied_by = assistant_id, applied_at = datetime.datetime.now())
    db.session.add(new_log)
    db.session.commit()

    return jsonify({
        'message': f'Treatment {treatment_id} successfully applied to Patient {patient_id} by Assistant {assistant_id}',
        'status': patient_treatment.status,
        'applied_at': patient_treatment.applied_at
    }), 200

