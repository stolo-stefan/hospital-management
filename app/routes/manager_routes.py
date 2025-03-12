from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import User
from app import db
from app.utils import check_json, get_user_by_id, check_role, update_user_fields

manager_bp = Blueprint('manager_bp', __name__)

@manager_bp.route('/', methods=['GET'])
@jwt_required()
def get_managers():
    """
    [GET] Retrieves all users with role 'General Manager'. Only General Manager can view.
    - Fetches all users who hold the 'General Manager' role.
    - If no managers are found, returns an appropriate message.
    Returns a JSON response with a list of general managers.
    """
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    managers = User.query.filter_by(role='General Manager').all()
    if not managers:
        return jsonify({'message': 'No managers found'}), 204
    return jsonify({'managers': [{'id': m.id, 'name': m.name} for m in managers]}), 200


@manager_bp.route('/<int:manager_id>', methods=['PUT'])
@jwt_required()
def update_manager(manager_id):
    """
    [PUT] Updates an existing manager's data. Only General Manager can do this.
    - Requires at least one field to be updated ('name', 'password', or 'role').
    - Checks if the provided manager ID exists and belongs to the 'General Manager' role.
    - If valid, updates the manager's details.
    Returns a JSON response confirming the update.
    """
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    manager = get_user_by_id(manager_id)
    if not manager or manager.role != 'General Manager':
        return jsonify({'error': 'Manager not found or invalid role'}), 404

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data
    if all(field not in data for field in ['name', 'password', 'role']):
        return jsonify({'error': 'At least one field (name, password, role) is required'}), 400

    update_user_fields(manager, data)
    db.session.commit()
    return jsonify({'message': 'Manager updated'})

@manager_bp.route('/<int:manager_id>', methods=['DELETE'])
@jwt_required()
def delete_manager(manager_id):
    """
    [DELETE] Deletes a manager by ID. Only General Manager can do this.
    - Checks if the provided manager ID exists.
    - If valid, removes the manager from the database.
    Returns a JSON response confirming the deletion.
    """
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    manager = get_user_by_id(manager_id)
    if not manager:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(manager)
    db.session.commit()
    return jsonify({'message': f'User {manager} deleted successfully'}), 200