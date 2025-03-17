import pytest
import json
from app.models import User

def test_register_doctor(client, auth_headers_manager):
    response = client.post('api/auth/register', headers=auth_headers_manager, json={
        "name": "new_doctor",
        "password": "doctorpassword",
        "role": "Doctor"
    })
    assert response.status_code == 201
    assert "User new_doctor - Role Doctor registered" in response.json["message"]

def test_get_all_doctors(client, auth_headers_manager, doctor):
    response = client.get('/api/doctors/', headers=auth_headers_manager)
    assert response.status_code == 200
    assert isinstance(response.json["doctors"], list)
    assert any(d["name"] == "doctor1" for d in response.json["doctors"])

def test_get_all_doctors_no_data(client, auth_headers_manager):
    response = client.get('/api/doctors/', headers=auth_headers_manager)
    assert response.status_code == 204  # No doctors found

def test_get_all_doctors_unauthorized(client):
    response = client.get('/api/doctors/')  # No auth headers
    assert response.status_code == 401

def test_update_doctor(client, auth_headers_manager, doctor):
    response = client.put(f'/api/doctors/{doctor.id}', headers=auth_headers_manager, json={
        "name": "updated_doctor"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Doctor updated"

def test_update_non_existent_doctor(client, auth_headers_manager):
    response = client.put('/api/doctors/9999', headers=auth_headers_manager, json={
        "name": "fake_doctor"
    })
    assert response.status_code == 404  # Doctor not found

def test_update_doctor_unauthorized(client, doctor):
    response = client.put(f'/api/doctors/{doctor.id}', json={"name": "hack_doctor"})
    assert response.status_code == 401  # Unauthorized

def test_delete_doctor(client, auth_headers_manager, doctor):
    response = client.delete(f'/api/doctors/{doctor.id}', headers=auth_headers_manager)
    assert response.status_code == 200
    assert response.json["message"] == "Doctor deleted successfully"

def test_delete_non_existent_doctor(client, auth_headers_manager):
    response = client.delete('/api/doctors/9999', headers=auth_headers_manager)
    assert response.status_code == 404  # Doctor not found

def test_delete_doctor_unauthorized(client, doctor):
    response = client.delete(f'/api/doctors/{doctor.id}')
    assert response.status_code == 401
