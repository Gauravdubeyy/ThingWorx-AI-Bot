import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("Test 1 — Health Check:")
    r1 = requests.get(f"{BASE_URL}/")
    print(json.dumps(r1.json(), indent=2))
    print("\n" + "="*50 + "\n")

    print("Test 2 — Basic question from the manual:")
    payload2 = {"message": "What are the minimum hardware requirements?"}
    r2 = requests.post(f"{BASE_URL}/chat", json=payload2)
    resp2 = r2.json()
    print(json.dumps(resp2, indent=2))
    session_id = resp2.get("session_id")
    print("\n" + "="*50 + "\n")

    if session_id:
        print("Test 3 — Follow-up question (session continuity):")
        payload3 = {
            "message": "What operating systems are supported?",
            "session_id": session_id
        }
        r3 = requests.post(f"{BASE_URL}/chat", json=payload3)
        print(json.dumps(r3.json(), indent=2))
        print("\n" + "="*50 + "\n")
    else:
        print("Skipping Test 3: No session_id from Test 2")

    print("Test 4 — Out of scope question:")
    payload4 = {"message": "What is the price of the Viatras system?"}
    r4 = requests.post(f"{BASE_URL}/chat", json=payload4)
    print(json.dumps(r4.json(), indent=2))
    print("\n" + "="*50 + "\n")

    print("Test 5 — Empty message validation:")
    payload5 = {"message": ""}
    r5 = requests.post(f"{BASE_URL}/chat", json=payload5)
    print(f"Status Code: {r5.status_code}")
    print(json.dumps(r5.json(), indent=2))

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Error running tests: {e}")
