import urllib.request
import json

req = urllib.request.Request(
    'http://localhost:8000/api/ai/chat/',
    data=b'{"messages": [{"role": "user", "content": "Que fait cette machine ?"}], "context": {"machine": "OSM-001"}}',
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as res:
        print("Status:", res.status)
        print("Response:", res.read().decode())
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print("Body:", e.read().decode())
