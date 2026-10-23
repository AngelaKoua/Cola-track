import requests

payload = {
    "ligne": "Ligne 2",
    "equipement": "TestEq",
    "type_incident": "Panne",
    "criticite": "Moyen",
    "description_probleme": "Test CORS",
    "responsable": "abdoul",
    "deadline": "2026-03-25"
}
try:
    res = requests.post("http://localhost:8000/api/incidents", json=payload, allow_redirects=False)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
