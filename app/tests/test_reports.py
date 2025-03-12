import pytest
import json

def test_doctor_patient_report(client, auth_headers_manager, doctor_assistant_patient_association):
    response = client.get('/api/reports/doctors-patients', headers=auth_headers_manager)
    assert response.status_code == 200
    assert "report" in response.json

def test_doctor_patient_report_unauthorized(client):
    response = client.get('/api/reports/doctors-patients')
    assert response.status_code == 401  # Should be unauthorized

def test_patient_treatment_report(client, auth_headers_doctor, doctor_assistant_patient_association, patient_treatment_assosciation):
    response = client.get(f'/api/reports/patient-treatments/{patient_treatment_assosciation.patient_id}', headers=auth_headers_doctor)
    assert response.status_code == 200  # Doctor should be able to access
    assert "treatments" in response.json  # Should contain treatments history

def test_patient_treatment_report_unauthorized(client, patient_treatment_assosciation):
    response = client.get(f'/api/reports/patient-treatments/{patient_treatment_assosciation.patient_id}')
    assert response.status_code == 401  # Should be unauthorized

def test_patient_treatment_report_forbidden(client, auth_headers_doctor, patient):
    response = client.get(f'/api/reports/patient-treatments/{patient.id}', headers=auth_headers_doctor)
    assert response.status_code == 403  # Doctor should be forbidden if they don’t supervise the patient
