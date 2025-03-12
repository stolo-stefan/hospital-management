import pytest
import json
from app.models import Treatment

def test_register_treatment(client, auth_headers_manager):
    response = client.post('/api/treatments/register', headers=auth_headers_manager, json={
        "name": "Chemotherapy",
        "description": "Cancer treatment"
    })
    assert response.status_code == 201
    assert "Treatment created successfully" in response.json["message"]

def test_register_treatment_missing_fields(client, auth_headers_manager):
    response = client.post('/api/treatments/register', headers=auth_headers_manager, json={
        "name": "Radiation Therapy"
    })  # Missing description
    assert response.status_code == 400  # Bad Request

def test_register_treatment_unauthorized(client):
    response = client.post('/api/treatments/register', json={"name": "Therapy", "description": "Mental health therapy"})
    assert response.status_code == 401  # Unauthorized

def test_get_all_treatments(client, auth_headers_manager, treatment):
    response = client.get('/api/treatments/', headers=auth_headers_manager) 
    assert response.status_code == 200
    assert isinstance(response.json["treatments"], list)
    assert any(t["name"] == "Physical Therapy" for t in response.json["treatments"])

def test_get_all_treatments_no_data(client, auth_headers_manager):
    response = client.get('/api/treatments/', headers=auth_headers_manager) 
    assert response.status_code == 204  # No treatments found

def test_get_treatment_by_id(client, auth_headers_manager, treatment):
    response = client.get(f'/api/treatments/{treatment.id}', headers=auth_headers_manager)
    assert response.status_code == 200
    assert response.json["name"] == "Physical Therapy"

def test_get_non_existent_treatment(client, auth_headers_manager):
    response = client.get('/api/treatments/9999', headers=auth_headers_manager)
    assert response.status_code == 404  # Treatment not found

def test_update_treatment(client, auth_headers_manager, treatment):
    response = client.put(f'/api/treatments/{treatment.id}', headers=auth_headers_manager, json={
        "name": "Updated Therapy"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Treatment updated successfully"

def test_update_non_existent_treatment(client, auth_headers_manager):
    response = client.put('/api/treatments/9999', headers=auth_headers_manager, json={
        "name": "Fake Therapy"
    })
    assert response.status_code == 404

def test_delete_treatment(client, auth_headers_manager, treatment):
    response = client.delete(f'/api/treatments/{treatment.id}', headers=auth_headers_manager)
    assert response.status_code == 200
    assert response.json["message"] == "Treatment deleted successfully"

def test_delete_non_existent_treatment(client, auth_headers_manager):
    response = client.delete('/api/treatments/9999', headers=auth_headers_manager)
    assert response.status_code == 404 

def test_prescribe_treatment(client, auth_headers_doctor, treatment, patient, doctor_assistant_patient_association):
    response = client.post(f'/api/treatments/{treatment.id}/prescribe/{patient.id}', headers=auth_headers_doctor)
    assert response.status_code == 201
    assert response.json["message"] == f'Treatment {treatment.id} prescribed to Patient {doctor_assistant_patient_association.patient_id} by Doctor {doctor_assistant_patient_association.doctor_id}'

def test_prescribe_treatment_non_existent_patient(client, auth_headers_doctor, treatment, doctor_assistant_patient_association):
    response = client.post(f'/api/treatments/{treatment.id}/prescribe/9999', headers=auth_headers_doctor)
    assert response.status_code == 404  # Patient not found

def test_prescribe_treatment_unauthorized(client, treatment, patient):
    response = client.post(f'/api/treatments/{treatment.id}/prescribe/{patient.id}')
    assert response.status_code == 401  # Unauthorized

def test_apply_treatment(client, auth_headers_assistant, treatment, patient, doctor_assistant_patient_association, patient_treatment_assosciation):
    response = client.post(f'/api/treatments/{treatment.id}/apply/{patient.id}', headers=auth_headers_assistant)
    assert response.status_code == 200
    assert response.json["message"] == f'Treatment {treatment.id} successfully applied to Patient {patient.id} by Assistant {doctor_assistant_patient_association.assistant_id}'

def test_apply_treatment_non_existent_patient(client, auth_headers_assistant, treatment):
    response = client.post(f'/api/treatments/{treatment.id}/apply/9999', headers=auth_headers_assistant)
    assert response.status_code == 404  # Patient not found
