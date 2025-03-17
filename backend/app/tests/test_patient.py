import pytest
import json
from app.models import User

def test_register_patient(client, auth_headers_manager):
    response = client.post('/api/patients/register', headers=auth_headers_manager, json={
        "name": "new_patient"
    })
    assert response.status_code == 201
    assert "Patient created successfully" in response.json["message"]

def test_register_patient_missing_name(client, auth_headers_manager):
    response = client.post('/api/patients/register', headers=auth_headers_manager, json={})
    assert response.status_code == 400

def test_register_patient_unauthorized(client):
    response = client.post('/api/patients/register', json={"name": "new_patient"})
    assert response.status_code == 401

def test_get_all_patients(client, auth_headers_manager, patient):
    response = client.get('/api/patients/', headers=auth_headers_manager)  
    assert response.status_code == 200
    assert isinstance(response.json["patients"], list)
    assert any(p["name"] == "patient1" for p in response.json["patients"])

def test_get_all_patients_no_data(client, auth_headers_manager):
    response = client.get('/api/patients/', headers=auth_headers_manager)
    assert response.status_code == 204  # No patients found

def test_get_patient_by_id(client, auth_headers_manager, patient):
    response = client.get(f'/api/patients/{patient.id}', headers=auth_headers_manager)
    assert response.status_code == 200
    assert response.json["name"] == "patient1"

def test_get_non_existent_patient(client, auth_headers_manager):
    response = client.get('/api/patients/9999', headers=auth_headers_manager)
    assert response.status_code == 404  # Patient not found

def test_update_patient(client, auth_headers_manager, patient):
    response = client.put(f'/api/patients/{patient.id}', headers=auth_headers_manager, json={
        "name": "updated_patient"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Patient updated successfully"

def test_update_non_existent_patient(client, auth_headers_manager):
    response = client.put('/api/patients/9999', headers=auth_headers_manager, json={
        "name": "fake_patient"
    })
    assert response.status_code == 404  # Patient not found

def test_update_patient_unauthorized(client, patient):
    response = client.put(f'/api/patients/{patient.id}', json={"name": "hack_patient"})
    assert response.status_code == 401 

def test_delete_patient(client, auth_headers_manager, patient):
    response = client.delete(f'/api/patients/{patient.id}', headers=auth_headers_manager)
    assert response.status_code == 200
    assert response.json["message"] == "Patient deleted successfully"

def test_delete_non_existent_patient(client, auth_headers_manager):
    response = client.delete('/api/patients/9999', headers=auth_headers_manager)
    assert response.status_code == 404

def test_delete_patient_unauthorized(client, patient):
    assert patient is not None, "Patient fixture returned None"
    response = client.delete(f'/api/patients/{patient.id}')
    assert response.status_code == 401
