import requests

try:
    resp = requests.get("http://localhost:8000/docs")
    print(f"Server is alive: {resp.status_code}")
except Exception as e:
    print(f"Server is down: {e}")
