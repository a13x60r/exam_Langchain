import argparse
import requests
import sys
import os

# Configuration
DEFAULT_BASE_URL = "http://main:8001"
DEFAULT_AUTH_URL = "http://auth:8000"

def get_token(username, password, auth_url):
    """Authenticate and return a bearer token."""
    try:
        # Try login first
        resp = requests.post(f"{auth_url}/login", json={"username": username, "password": password})
        if resp.status_code == 200:
            return resp.json()["access_token"]
        
        # If login fails, straightforwardly try signup (for convenience in this exam context)
        # Note: In a real app, we'd handle this more carefully.
        print("Login failed, attempting signup...")
        resp = requests.post(f"{auth_url}/signup", json={"username": username, "password": password})
        if resp.status_code == 200:
            print("Signup successful.")
            # Login again
            resp = requests.post(f"{auth_url}/login", json={"username": username, "password": password})
            if resp.status_code == 200:
                return resp.json()["access_token"]
        
        print(f"Authentication failed: {resp.text}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Connection error during auth: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="LangChain Assistant CLI Client")
    parser.add_argument("--mode", required=True, choices=["analyze", "generate", "explain", "pipeline"], help="Action to perform")
    parser.add_argument("--file", required=True, help="Path to the code file")
    parser.add_argument("--username", default="cli_user", help="Username for auth")
    parser.add_argument("--password", default="cli_pass", help="Password for auth")
    parser.add_argument("--api_url", default=DEFAULT_BASE_URL, help="Main API URL")
    parser.add_argument("--auth_url", default=DEFAULT_AUTH_URL, help="Auth API URL")

    args = parser.parse_args()

    # Read file
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    with open(args.file, "r") as f:
        content = f.read()

    # Authenticate
    token = get_token(args.username, args.password, args.auth_url)
    headers = {"Authorization": f"Bearer {token}"}

    # Prepare payload (TestExplanation expects 'test_code', others 'code')
    if args.mode == "explain":
        payload = {"test_code": content}
        endpoint = "/explain_test"
    elif args.mode == "pipeline":
        payload = {"code": content}
        endpoint = "/full_pipeline"
    elif args.mode == "generate":
        payload = {"code": content}
        endpoint = "/generate_test"
    else: # analyze
        payload = {"code": content}
        endpoint = "/analyze"

    # Execute
    try:
        url = f"{args.api_url}{endpoint}"
        print(f"Sending request to {url}...")
        resp = requests.post(url, json=payload, headers=headers)
        
        if resp.status_code == 200:
            print("\n--- Response ---")
            print(resp.json())
        else:
            print(f"Error {resp.status_code}: {resp.text}")
    
    except requests.RequestException as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    main()
