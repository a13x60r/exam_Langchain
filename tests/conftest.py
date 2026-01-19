import pytest
import os
import sys

# Add project root to the path so src imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys
from unittest.mock import MagicMock

# Mock module langchain_groq if not installed
try:
    import langchain_groq
except ImportError:
    sys.modules["langchain_groq"] = MagicMock()

# Mock passlib if not installed (for auth tests running in main container)
try:
    import passlib
except ImportError:
    sys.modules["passlib"] = MagicMock()
    sys.modules["passlib.context"] = MagicMock()

# Set environment variables for testing BEFORE importing any modules
os.environ["GROQ_API_KEY"] = "dummy_key"
os.environ["AUTH_SERVICE_URL"] = "http://test-auth-service"
os.environ["MAIN_SERVICE_URL"] = "http://test-main-service"

@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Mock environment variables for testing.
    """
    monkeypatch.setenv("AUTH_SERVICE_URL", "http://test-auth-service")
    monkeypatch.setenv("MAIN_SERVICE_URL", "http://test-main-service")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
