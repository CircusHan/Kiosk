import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_reception_departments():
    res = client.get("/api/reception/departments")
    assert res.status_code == 200
    departments = res.json()
    assert isinstance(departments, list)
    assert departments

# === Tests for Web, Settings, and Voice Interaction Endpoints ===

from unittest.mock import patch, MagicMock, AsyncMock # Import AsyncMock
from app.api.endpoints.web import api_key_storage # For direct manipulation

# Helper to manage api_key_storage for tests
def clear_api_key_storage():
    api_key_storage.clear()

def set_api_key(key: str):
    clear_api_key_storage()
    api_key_storage['gemini_api_key'] = key

def test_get_settings_page():
    clear_api_key_storage()
    response = client.get("/settings")
    assert response.status_code == 200
    assert "Settings" in response.text
    assert "Gemini API Key" in response.text

def test_post_settings_save_key():
    clear_api_key_storage()
    response = client.post("/settings", data={"gemini_api_key": "test_key_123"})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response.get("message") == "API Key saved successfully!"
    assert api_key_storage.get("gemini_api_key") == "test_key_123"
    clear_api_key_storage() # Clean up

def test_post_settings_missing_key():
    clear_api_key_storage()
    response = client.post("/settings", data={}) # No key
    assert response.status_code == 400
    json_response = response.json()
    # FastAPI can return detail or message, checking both
    error_message = json_response.get("message", json_response.get("detail", ""))
    assert "API Key is required" in error_message

def test_get_voice_interaction_page():
    clear_api_key_storage()
    response = client.get("/voice-interaction")
    assert response.status_code == 200
    assert "Voice Interaction" in response.text
    assert "Start Listening" in response.text # Check for a button

@patch('app.api.endpoints.web.genai.GenerativeModel')
def test_post_voice_command_success(mock_generative_model):
    set_api_key('fake_gemini_key_success') # Setup API key

    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mocked AI response"
    # Use AsyncMock for the async method
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)
    mock_generative_model.return_value = mock_model_instance

    response = client.post("/api/voice_command", json={"text": "Hello AI"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["user_text"] == "Hello AI"
    assert json_response["ai_response"] == "Mocked AI response"

    # Verify genai.configure was called (implicitly, by checking model init and method call)
    # genai.configure is called before model instantiation in the endpoint.
    # A more direct way to check genai.configure would be to patch 'app.api.endpoints.web.genai.configure'
    mock_generative_model.assert_called_once_with('gemini-pro')
    mock_model_instance.generate_content_async.assert_called_once_with("Hello AI")
    clear_api_key_storage() # Clean up

def test_post_voice_command_no_api_key():
    clear_api_key_storage() # Ensure no API key
    response = client.post("/api/voice_command", json={"text": "Hello AI without key"})
    assert response.status_code == 401
    json_response = response.json()
    assert "API key not configured" in json_response.get("error", "")

@patch('app.api.endpoints.web.genai.GenerativeModel')
def test_post_voice_command_gemini_api_error(mock_generative_model):
    set_api_key('fake_gemini_key_error') # Setup API key

    mock_model_instance = MagicMock()
    # Use AsyncMock for the async method that raises an exception
    mock_model_instance.generate_content_async = AsyncMock(side_effect=Exception("Gemini network error"))
    mock_generative_model.return_value = mock_model_instance

    response = client.post("/api/voice_command", json={"text": "Hello AI, expect error"})
    assert response.status_code == 500
    json_response = response.json()
    assert "Error processing your request with AI" in json_response.get("error", "")
    assert "Gemini network error" in json_response.get("error", "") # Check if specific error is propagated (as per current code)
    clear_api_key_storage() # Clean up

@patch('app.api.endpoints.web.genai.configure')
@patch('app.api.endpoints.web.genai.GenerativeModel')
def test_post_voice_command_genai_configure_called(mock_generative_model, mock_genai_configure):
    # More specific test to ensure genai.configure is called with the API key
    set_api_key('specific_test_key_for_configure')

    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "AI response for configure test"
    # Use AsyncMock for the async method
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)
    mock_generative_model.return_value = mock_model_instance

    client.post("/api/voice_command", json={"text": "Test configure call"})

    mock_genai_configure.assert_called_once_with(api_key='specific_test_key_for_configure')
    clear_api_key_storage()
