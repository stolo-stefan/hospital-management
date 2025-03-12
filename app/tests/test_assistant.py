import pytest
import json
from app.models import User

def test_get_all_assistants(client, auth_headers_manager, assistant):
    response = client.get('/api/assistants/', headers=auth_headers_manager)
    assert response.status_code == 200
    assert isinstance(response.json["assistants"], list)
    assert any(a["name"] == "assistant1" for a in response.json["assistants"])

def test_get_all_assistants_no_data(client, auth_headers_manager):
    response = client.get('/api/assistants/', headers=auth_headers_manager)
    assert response.status_code == 204  # No assistants found

def test_get_all_assistants_unauthorized(client):
    response = client.get('/api/assistants/')
    assert response.status_code == 401  # Unauthorized

def test_update_assistant(client, auth_headers_manager, assistant):
    response = client.put(f'/api/assistants/{assistant.id}', headers=auth_headers_manager, json={
        "name": "updated_assistant"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Assistant updated"

def test_update_non_existent_assistant(client, auth_headers_manager):
    response = client.put('/api/assistants/9999', headers=auth_headers_manager, json={
        "name": "fake_assistant"
    })
    assert response.status_code == 404  # Assistant not found

def test_update_assistant_unauthorized(client, assistant):
    response = client.put(f'/api/assistants/{assistant.id}', json={"name": "hack_assistant"})
    assert response.status_code == 401  # Unauthorized

def test_delete_assistant(client, auth_headers_manager, assistant):
    response = client.delete(f'/api/assistants/{assistant.id}', headers=auth_headers_manager)
    assert response.status_code == 200
    assert response.json["message"] == "Assistant deleted successfully"

def test_delete_non_existent_assistant(client, auth_headers_manager):
    response = client.delete('/api/assistants/9999', headers=auth_headers_manager)
    assert response.status_code == 404  # Assistant not found

def test_delete_assistant_unauthorized(client, assistant, unauthorized_headers):
    response = client.delete(f'/api/assistants/{assistant.id}', headers=unauthorized_headers)
    assert response.status_code == 401  # Unauthorized
