import pytest
import json
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

def test_login_success(client, test_user):
    response = client.post('/api/auth/login', json={"name": "testuser", "password": "testpassword"})
    data = json.loads(response.data)
    assert response.status_code == 200
    assert "access_token" in data

def test_login_wrong_password(client, test_user):
    response = client.post('/api/auth/login', json={"name": "testuser", "password": "wrongpassword"})
    data = json.loads(response.data)
    assert response.status_code == 401
    assert data["error"] == "Invalid password"

def test_login_user_not_found(client):
    response = client.post('/api/auth/login', json={"name": "unknownuser", "password": "testpassword"})
    data = json.loads(response.data)
    assert response.status_code == 404
    assert data["error"] == "User with this name was not found"

def test_login_missing_fields(client):
    response = client.post('/api/auth/login', json={"name": "testuser"})  # Missing password
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data["error"] == "Missing name or password"

def test_register_success(client, auth_headers_manager):
    response = client.post('/api/auth/register', headers=auth_headers_manager, json={
        "name": "newuser",
        "password": "newpassword",
        "role": "Doctor"
    })
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data["message"] == "User newuser - Role Doctor registered"

def test_register_non_manager(client, test_user, auth_headers_doctor):
    response = client.post('/api/auth/register', headers=auth_headers_doctor, json={
        "name": "newuser",
        "password": "newpassword",
        "role": "Doctor"
    })
    assert response.status_code == 401

def test_register_missing_fields(client, auth_headers_manager):
    response = client.post('/api/auth/register', headers=auth_headers_manager, json={
        "name": "newuser"
    })
    assert response.status_code == 400
    assert "error" in response.json

def test_register_duplicate_user(client, auth_headers_manager, test_user):
    response = client.post('/api/auth/register', headers=auth_headers_manager, json={
        "name": "testuser",
        "password": "anotherpassword",
        "role": "Doctor"
    })
    assert response.status_code == 400
