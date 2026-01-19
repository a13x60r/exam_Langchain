from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.authentication.auth import app

client = TestClient(app)

def test_signup_flow():
    # 1. Signup
    response = client.post("/signup", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    
    # 2. Duplicate signup
    response = client.post("/signup", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 400

@patch("src.api.authentication.auth.verify_password")
@patch("src.api.authentication.auth.get_password_hash")
def test_login_flow(mock_hash, mock_verify):
    # Setup mocks
    mock_hash.side_effect = lambda p: f"hashed_{p}"
    
    # Configure verify to return True only if password is "securepass" (and hash matches)
    # But since we are mocking, we can just check the input password
    def verify_side_effect(plain, hashed):
        return plain == "securepass"
    mock_verify.side_effect = verify_side_effect

    # 1. Successful login (signup first to populate db)
    client.post("/signup", json={"username": "loginuser", "password": "securepass"})
    
    response = client.post("/login", json={"username": "loginuser", "password": "securepass"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]
    
    # 2. Verify token
    response = client.get("/me", params={"token": token})
    assert response.status_code == 200
    assert response.json()["username"] == "loginuser"
    
    # 3. Invalid password
    response = client.post("/login", json={"username": "loginuser", "password": "wrongpassword"})
    assert response.status_code == 401

def test_verify_token_invalid():
    response = client.get("/me", params={"token": "invalid_token"})
    assert response.status_code == 401
