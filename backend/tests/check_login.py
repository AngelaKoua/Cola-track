import os

import requests

def test_login():
    url = "http://localhost:8000/token"
    # Technician (password taken from the environment, never hardcoded)
    data = {"username": "technician", "password": os.environ.get("TEST_TECHNICIAN_PASSWORD", "")}
    try:
        response = requests.post(url, data=data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            print("Technician Login Success:", response.json().keys())
            print("Role:", response.json().get("role"))
        else:
            print("Technician Login Failed:", response.text)
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_login()
