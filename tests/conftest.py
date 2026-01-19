import pytest
import os
import sys

# Add src to the path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Mock environment variables for testing.
    """
    monkeypatch.setenv("AUTH_SERVICE_URL", "http://test-auth-service")
    monkeypatch.setenv("MAIN_SERVICE_URL", "http://test-main-service")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
