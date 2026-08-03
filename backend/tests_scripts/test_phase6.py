import urllib.request
import json
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def make_request(method, url, data=None, token=None, is_form=False):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = None
    if data is not None:
        if is_form:
            import urllib.parse as uparse
            encoded_data = uparse.urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            encoded_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
            
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 500, str(e)

def run_tests():
    print("--- Phase 6 Production-Ready Testing ---")
    
    # 1. Login
    email = f"prodtest_{uuid.uuid4().hex[:6]}@example.com"
    make_request("POST", f"{BASE_URL}/auth/register", data={"email": email, "full_name": "Prod Test", "password": "pass"})
    _, body = make_request("POST", f"{BASE_URL}/auth/login", data={"username": email, "password": "pass"}, is_form=True)
    token = json.loads(body).get("access_token")
    
    # 2. Setup WS & Project
    _, body = make_request("POST", f"{BASE_URL}/workspaces/", data={"name": "Prod WS"}, token=token)
    ws_id = json.loads(body).get("id")
    _, body = make_request("POST", f"{BASE_URL}/workspaces/{ws_id}/projects", data={"name": "Prod Project"}, token=token)
    proj_id = json.loads(body).get("id")

    print(f"\nCreated Workspace ({ws_id}) & Project ({proj_id})")

    # 3. Create a task without assignee
    print("\n--- Testing Task Creation (Without Assignee) ---")
    status, body = make_request("POST", f"{BASE_URL}/projects/{proj_id}/tasks", data={"title": "Task 1", "priority": "LOW"}, token=token)
    print(f"Status: {status} -> {json.loads(body).get('title')}")
    
    # 4. Fetch tasks to populate Cache
    print("\n--- Testing First Fetch (Cache Miss - hits DB) ---")
    t0 = time.time()
    status, body = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks", token=token)
    t1 = time.time()
    print(f"Status: {status} -> Fetched {len(json.loads(body))} tasks. Time taken: {(t1-t0)*1000:.2f} ms")
    
    # 5. Fetch tasks again (Should hit FakeRedis Cache)
    print("\n--- Testing Second Fetch (Cache Hit - hits Redis) ---")
    t0 = time.time()
    status, body = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks", token=token)
    t1 = time.time()
    print(f"Status: {status} -> Fetched {len(json.loads(body))} tasks. Time taken: {(t1-t0)*1000:.2f} ms")
    
    # 6. Create a task WITH assignee to test BackgroundTasks (Email Simulation)
    print("\n--- Testing Task Creation (WITH Assignee -> Triggers Background Email) ---")
    # For simplicity, assign to self
    user_id = json.loads(make_request("GET", f"{BASE_URL}/users/me", token=token)[1]).get("id")
    
    t0 = time.time()
    status, body = make_request("POST", f"{BASE_URL}/projects/{proj_id}/tasks", data={"title": "Task 2 assigned", "assignee_id": user_id}, token=token)
    t1 = time.time()
    print(f"Status: {status} -> {json.loads(body).get('title')}. Time taken to return (Email is backgrounded): {(t1-t0)*1000:.2f} ms")
    
    # 7. Fetch tasks again (Cache should be invalidated by step 6, so Cache Miss)
    print("\n--- Testing Fetch after Cache Invalidation ---")
    t0 = time.time()
    status, body = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks", token=token)
    t1 = time.time()
    print(f"Status: {status} -> Fetched {len(json.loads(body))} tasks. Time taken: {(t1-t0)*1000:.2f} ms")
    
if __name__ == "__main__":
    run_tests()
