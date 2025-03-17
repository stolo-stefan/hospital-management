from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required
from app.models import User
from app import db
from app.utils import check_json, get_user_by_id, check_role

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if "name" not in data or "password" not in data:
        return jsonify({"error": "Missing name or password"}), 400
    
    user = User.query.filter_by(name=data['name']).first()
    if not user:
        return jsonify({'error': 'User with this name was not found'}), 404
    if not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid password'}), 401
    
    token = create_access_token(identity={'id': user.id, 'role': user.role})
    return jsonify({'message': 'Login successful', 'access_token': token}), 200


@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    role_error = check_role(['General Manager'])
    if role_error:
        return role_error

    data = check_json()
    if isinstance(data, dict) and 'error' in data:
        return data

    if 'name' not in data or not data['name']:
        return jsonify({'error': 'Name field must be filled'}), 400
    if 'password' not in data or not data['password']:
        return jsonify({'error': 'Password field must be filled'}), 400
    if 'role' not in data or not data['role']:
        return jsonify({'error': 'Role field must be filled'}), 400

    if User.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'User with this name already exists'}), 400

    new_user = User(
        name=data['name'],
        role=data['role'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': f'User {new_user.name} - Role {new_user.role} registered'}), 201