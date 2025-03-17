from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import User
from app import db
from app.utils import check_json, get_user_by_id, check_role, update_user_fields

doctor_bp = Blueprint('doctor_bp', __name__)

@doctor_bp.route('/', methods=['GET'])
@jwt_required()
def get_doctors():
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    doctors = User.query.filter_by(role='Doctor').all()
    if not doctors:
        return jsonify({'message': 'No doctors found'}), 204
    return jsonify({'doctors': [{'id': d.id, 'name': d.name} for d in doctors]}), 200


@doctor_bp.route('/<int:doctor_id>', methods=['PUT'])
@jwt_required()
def update_doctor(doctor_id):
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    doctor = get_user_by_id(doctor_id)
    if not doctor or doctor.role != 'Doctor':
        return jsonify({'error': 'Doctor not found or invalid role'}), 404

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data
    if all(field not in data for field in ['name', 'password', 'role']):
        return jsonify({'error': 'At least one field (name, password, role) is required'}), 400

    update_user_fields(doctor, data)
    db.session.commit()
    return jsonify({'message': 'Doctor updated'})


@doctor_bp.route('/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(doctor_id):
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    doctor = get_user_by_id(doctor_id)
    if not doctor:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(doctor)
    db.session.commit()
    return jsonify({'message': 'Doctor deleted successfully'}), 200
