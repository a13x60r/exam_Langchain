from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.api.assistant.main import app, verify_token, AnalysisOutput
import pytest

client = TestClient(app)

# Bypass authentication by overriding dependency
async def mock_verify_token():
    return "testuser"

app.dependency_overrides[verify_token] = mock_verify_token

def test_analyze_endpoint():
    mock_result = AnalysisOutput(is_optimal=True, issues=[], suggestions=[])
    
    with patch("src.api.assistant.main.analysis_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_result
        response = client.post("/analyze", json={"code": "print('hello')"})
        assert response.status_code == 200
        assert response.json()["is_optimal"] is True

def test_generate_test_endpoint():
    mock_result = MagicMock()
    mock_result.test_code = "def test_x(): pass"
    
    with patch("src.api.assistant.main.test_generation_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_result
        response = client.post("/generate_test", json={"code": "def x(): pass"})
        assert response.status_code == 200
        assert response.json()["test_code"] == "def test_x(): pass"

def test_chat_endpoint():
    mock_response = MagicMock()
    mock_response.content = "Hello there!"
    
    with patch("src.api.assistant.main.chat_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_response
        response = client.post("/chat", json={"message": "Hi"})
        assert response.status_code == 200
        assert response.json()["response"] == "Hello there!"
