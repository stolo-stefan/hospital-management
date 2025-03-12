from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import User
from app import db
from app.utils import check_json, get_user_by_id, check_role, update_user_fields

assistant_bp = Blueprint('assistant_bp', __name__)

@assistant_bp.route('/', methods=['GET'])
@jwt_required()
def get_assistants():
    """
    [GET] Retrieves all users with role 'Assistant'. Only General Manager can view.
    - Fetches all users with the role of 'Assistant'.
    - If no assistants are found, returns an appropriate message.
    Returns a JSON response with a list of assistants.
    """
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    assistants = User.query.filter_by(role='Assistant').all()
    if not assistants:
        return jsonify({'message': 'No assistants found'}), 204
    return jsonify({'assistants': [{'id': a.id, 'name': a.name} for a in assistants]}), 200


@assistant_bp.route('/<int:assistant_id>', methods=['PUT'])
@jwt_required()
def update_assistant(assistant_id):
    """
    [PUT] Updates an existing assistant's data. Only General Manager can do this.
    - Requires at least one field to be updated ('name', 'password', or 'role').
    - Checks if the provided assistant ID exists and belongs to the 'Assistant' role.
    - If valid, updates the assistant's details.
    Returns a JSON response confirming the update.
    """
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    assistant = get_user_by_id(assistant_id)
    if not assistant or assistant.role != 'Assistant':
        return jsonify({'error': 'Assistant not found or invalid role'}), 404

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data
    if all(field not in data for field in ['name', 'password', 'role']):
        return jsonify({'error': 'At least one field (name, password, role) is required'}), 400

    update_user_fields(assistant, data)
    db.session.commit()
    return jsonify({'message': 'Assistant updated'})


@assistant_bp.route('/<int:assistant_id>', methods=['DELETE'])
@jwt_required()
def delete_assistant(assistant_id):
    """
    [DELETE] Deletes an assistant by ID. Only General Manager can do this.
    - Checks if the provided assistant ID exists.
    - If valid, removes the assistant from the database.
    Returns a JSON response confirming the deletion.
    """
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    assistant = get_user_by_id(assistant_id)
    if not assistant:
        return jsonify({'error': 'User not found'}), 404

    from app.models.patient_assistant import PatientAssistant
    PatientAssistant.query.filter_by(assistant_id=assistant.id).delete()
    db.session.commit()

    db.session.delete(assistant)
    db.session.commit()
    return jsonify({'message': 'Assistant deleted successfully'}), 200