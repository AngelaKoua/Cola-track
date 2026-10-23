import urllib.request
import json

req = urllib.request.Request(
    'http://localhost:8000/api/ai/chat/',
    data=b'{"messages": [{"role": "user", "content": "Quel mod\xc3\xa8le est utilis\xc3\xa9 pour la d\xc3\xa9tection des anomalies et comment sont prioris\xc3\xa9es les recommandations ?"}], "context": {}}',
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print("Body:", e.read().decode())
