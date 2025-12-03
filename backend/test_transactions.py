import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth/login"
TRANS_URL = f"{BASE_URL}/transactions/"

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

def create_transaction(headers):
    print("\n[TEST] Create Transaction")
    data = {
        "amount": 150.50,
        "category": "Test Category",
        "type": "expense",
        "description": "Test Transaction",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    response = requests.post(TRANS_URL, json=data, headers=headers)
    if response.status_code == 200:
        print("SUCCESS: Transaction created.")
        return response.json()
    else:
        print(f"FAILED: {response.status_code} - {response.text}")
        return None

def get_transactions(headers):
    print("\n[TEST] Get All Transactions")
    response = requests.get(TRANS_URL, headers=headers)
    if response.status_code == 200:
        txs = response.json()
        print(f"SUCCESS: Retrieved {len(txs)} transactions.")
        return txs
    else:
        print(f"FAILED: {response.status_code} - {response.text}")
        return []

def get_transaction_by_id(headers, tx_id):
    print(f"\n[TEST] Get Transaction {tx_id}")
    response = requests.get(f"{TRANS_URL}{tx_id}", headers=headers)
    if response.status_code == 200:
        print("SUCCESS: Transaction retrieved.")
        return response.json()
    else:
        print(f"FAILED: {response.status_code} - {response.text}")
        return None

def update_transaction(headers, tx_id):
    print(f"\n[TEST] Update Transaction {tx_id}")
    data = {
        "amount": 200.00,
        "description": "Updated Description"
    }
    response = requests.put(f"{TRANS_URL}{tx_id}", json=data, headers=headers)
    if response.status_code == 200:
        print("SUCCESS: Transaction updated.")
        return response.json()
    else:
        print(f"FAILED: {response.status_code} - {response.text}")
        return None

def delete_transaction(headers, tx_id):
    print(f"\n[TEST] Delete Transaction {tx_id}")
    response = requests.delete(f"{TRANS_URL}{tx_id}", headers=headers)
    if response.status_code == 200:
        print("SUCCESS: Transaction deleted.")
    else:
        print(f"FAILED: {response.status_code} - {response.text}")

def main():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create
    tx = create_transaction(headers)
    if not tx:
        return
    tx_id = tx["id"]

    # 2. Get All
    get_transactions(headers)

    # 3. Get One
    get_transaction_by_id(headers, tx_id)

    # 4. Update
    updated_tx = update_transaction(headers, tx_id)
    if updated_tx and updated_tx["amount"] == 200.00:
        print("VERIFIED: Amount updated correctly.")

    # 5. Delete
    delete_transaction(headers, tx_id)

    # 6. Verify Deletion
    print("\n[TEST] Verify Deletion")
    response = requests.get(f"{TRANS_URL}{tx_id}", headers=headers)
    if response.status_code == 404:
        print("SUCCESS: Transaction not found (as expected).")
    else:
        print(f"FAILED: Transaction still exists or other error: {response.status_code}")

if __name__ == "__main__":
    main()
