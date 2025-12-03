import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"

def get_token():
    print("Logging in...")
    response = requests.post(AUTH_URL, data={
        "username": "hello@gmail.com",
        "password": "Remo@KA@12"
    })
    if response.status_code == 200:
        print("Login successful.")
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        exit(1)

def print_response(method, url, resp):
    print(f"{method} {url}: {resp.status_code}")
    if resp.status_code >= 400:
        print(f"ERROR DETAILS: {resp.text}")

def test_dashboard(headers):
    print("\n--- Testing Dashboard Endpoints ---")
    
    # Summary
    resp = requests.get(f"{BASE_URL}/dashboard/summary", headers=headers)
    print_response("GET", "/dashboard/summary", resp)
    
    # Trends
    resp = requests.get(f"{BASE_URL}/dashboard/trends", headers=headers)
    print_response("GET", "/dashboard/trends", resp)
    
    # Category Analysis
    resp = requests.get(f"{BASE_URL}/dashboard/category-analysis", headers=headers)
    print_response("GET", "/dashboard/category-analysis", resp)

def test_goals(headers):
    print("\n--- Testing Goals Endpoints ---")
    
    # Create Goal
    goal_data = {
        "title": "Test Goal",
        "target_amount": 1000.0,
        "target_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "description": "Test Description"
    }
    resp = requests.post(f"{BASE_URL}/goals/", json=goal_data, headers=headers)
    print_response("POST", "/goals/", resp)
    
    if resp.status_code == 200:
        goal_id = resp.json()["id"]
        
        # Get All Goals
        resp = requests.get(f"{BASE_URL}/goals/", headers=headers)
        print_response("GET", "/goals/", resp)
        
        # Get Single Goal
        resp = requests.get(f"{BASE_URL}/goals/{goal_id}", headers=headers)
        print_response("GET", f"/goals/{goal_id}", resp)
        
        # Add Amount
        resp = requests.post(f"{BASE_URL}/goals/{goal_id}/add-amount?amount=100", headers=headers)
        print_response("POST", f"/goals/{goal_id}/add-amount", resp)
        
        # Delete Goal
        resp = requests.delete(f"{BASE_URL}/goals/{goal_id}", headers=headers)
        print_response("DELETE", f"/goals/{goal_id}", resp)

def test_predictions(headers):
    print("\n--- Testing Predictions Endpoints ---")
    
    # Budget Prediction
    resp = requests.get(f"{BASE_URL}/predictions/budget", headers=headers)
    print_response("GET", "/predictions/budget", resp)
    
    # Trends
    resp = requests.get(f"{BASE_URL}/predictions/trends", headers=headers)
    print_response("GET", "/predictions/trends", resp)
    
    # Forecast
    resp = requests.get(f"{BASE_URL}/predictions/forecast", headers=headers)
    print_response("GET", "/predictions/forecast", resp)

def test_badges(headers):
    print("\n--- Testing Badges Endpoints ---")
    
    # Get User Badges
    resp = requests.get(f"{BASE_URL}/badges/", headers=headers)
    print_response("GET", "/badges/", resp)
    
    # Get Available Badges
    resp = requests.get(f"{BASE_URL}/badges/available", headers=headers)
    print_response("GET", "/badges/available", resp)

def main():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    test_dashboard(headers)
    test_goals(headers)
    test_predictions(headers)
    test_badges(headers)

if __name__ == "__main__":
    main()
