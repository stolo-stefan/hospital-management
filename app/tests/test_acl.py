import pytest

def test_manager_access(client, auth_headers_manager):
    response = client.get('/api/doctors/', headers=auth_headers_manager)
    assert response.status_code != 401  # Manager should be authorized

def test_doctor_cannot_access_manager_endpoints(client, auth_headers_doctor):
    response = client.get('/api/doctors/', headers=auth_headers_doctor)
    assert response.status_code == 401  # Doctors should be unauthorized

def test_assistant_cannot_access_manager_endpoints(client, auth_headers_assistant):
    response = client.get('/api/doctors/', headers=auth_headers_assistant)
    assert response.status_code == 401  # Assistants should be unauthorized

def test_unauthorized_user_cannot_access_protected_endpoints(client, unauthorized_headers):
    response = client.get('/api/doctors/', headers=unauthorized_headers)
    assert response.status_code == 401  # Unauthorized users should be rejected

def test_doctor_can_register_patient(client, auth_headers_doctor):
    response = client.post('/api/patients/register', headers=auth_headers_doctor, json={"name": "New Patient"})
    assert response.status_code == 201  # Doctor should be able to register patients

def test_assistant_cannot_register_patient(client, auth_headers_assistant):
    response = client.post('/api/patients/register', headers=auth_headers_assistant, json={"name": "New Patient"})
    assert response.status_code == 401  # Assistants should be unauthorized

def test_doctor_can_prescribe_treatment(client, auth_headers_doctor, treatment, patient, doctor_assistant_patient_association):
    response = client.post(f'/api/treatments/{treatment.id}/prescribe/{patient.id}', headers=auth_headers_doctor)
    assert response.status_code == 201  # Doctor should be able to prescribe treatments

def test_assistant_cannot_prescribe_treatment(client, auth_headers_assistant, treatment, patient):
    response = client.post(f'/api/treatments/{treatment.id}/prescribe/{patient.id}', headers=auth_headers_assistant)
    assert response.status_code == 401  # Assistants should be unauthorized

def test_assistant_can_apply_treatment(client, auth_headers_assistant, treatment, patient, doctor_assistant_patient_association, patient_treatment_assosciation):
    response = client.post(f'/api/treatments/{treatment.id}/apply/{patient.id}', headers=auth_headers_assistant)
    assert response.status_code == 200  # Assistant should be able to apply treatments

def test_doctor_cannot_apply_treatment(client, auth_headers_doctor, treatment, patient):
    response = client.post(f'/api/treatments/{treatment.id}/apply/{patient.id}', headers=auth_headers_doctor)
    assert response.status_code == 403  # Doctors should not be authorized to apply treatments
