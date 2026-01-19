def test_environment_vars(mock_env_vars):
    import os
    assert os.getenv("AUTH_SERVICE_URL") == "http://test-auth-service"
    assert os.getenv("MAIN_SERVICE_URL") == "http://test-main-service"

def test_basic_math():
    assert 1 + 1 == 2
