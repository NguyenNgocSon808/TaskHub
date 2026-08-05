import json
import urllib.request
import urllib.parse
import urllib.error
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
        start = time.time()
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            end = time.time()
            process_time = response.getheader('X-Process-Time', 'N/A')
            return response.status, body, (end - start) * 1000, process_time
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8"), 0, 'N/A'
    except Exception as e:
        return 500, str(e), 0, 'N/A'

def run_e2e():
    print("=== TASKHUB E2E TESTING ===")
    
    # 1. Register
    email = f"e2e_{int(time.time())}@example.com"
    status, body, _, _ = make_request("POST", f"{BASE_URL}/auth/register", {
        "email": email,
        "password": "password123",
        "full_name": "E2E User"
    })
    print(f"Register [{status}]:", body)
    
    # 2. Login
    status, body, _, _ = make_request("POST", f"{BASE_URL}/auth/login", {
        "username": email,
        "password": "password123"
    }, is_form=True)
    print(f"Login [{status}]: Success")
    token = json.loads(body).get("access_token")
    
    # 3. Create Workspace
    status, body, _, _ = make_request("POST", f"{BASE_URL}/workspaces/", {
        "name": "E2E Workspace",
        "description": "Workspace for E2E testing"
    }, token=token)
    print(f"Create Workspace [{status}]:", body)
    ws_id = json.loads(body).get("id")
    
    # 4. Create Project
    status, body, _, _ = make_request("POST", f"{BASE_URL}/workspaces/{ws_id}/projects", {
        "name": "E2E Project",
        "description": "Project for E2E testing"
    }, token=token)
    print(f"Create Project [{status}]:", body)
    proj_id = json.loads(body).get("id")
    
    # 5. Create Task
    status, body, _, pt = make_request("POST", f"{BASE_URL}/projects/{proj_id}/tasks", {
        "title": "E2E Task",
        "description": "Task for E2E testing",
        "status": "TODO",
        "priority": "HIGH"
    }, token=token)
    print(f"Create Task [{status}]: Server Process Time: {pt}s")
    task_id = json.loads(body).get("id")
    
    # 6. Fetch Tasks (Cache Miss)
    print("\n--- Testing Cache Miss ---")
    status, body, t_total, pt = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks", token=token)
    print(f"Fetch 1 [{status}]: Returned {len(json.loads(body))} tasks. Server Process Time: {pt}s. Total Time: {t_total:.2f}ms")
    
    # 7. Fetch Tasks (Cache Hit)
    print("\n--- Testing Cache Hit ---")
    status, body, t_total, pt = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks", token=token)
    print(f"Fetch 2 [{status}]: Returned {len(json.loads(body))} tasks. Server Process Time: {pt}s. Total Time: {t_total:.2f}ms")
    
    # 8. Update Task (Invalidates Cache)
    status, body, _, pt = make_request("PATCH", f"{BASE_URL}/tasks/{task_id}", {
        "status": "DONE"
    }, token=token)
    print(f"\nUpdate Task [{status}]: Server Process Time: {pt}s")
    
    # 9. Fetch Tasks (Cache Miss due to invalidation)
    print("\n--- Testing Cache Miss after Update ---")
    status, body, t_total, pt = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks", token=token)
    tasks = json.loads(body)
    print(f"Fetch 3 [{status}]: Returned {len(tasks)} tasks. First task status: {tasks[0]['status']}. Server Process Time: {pt}s. Total Time: {t_total:.2f}ms")

if __name__ == "__main__":
    time.sleep(2) # wait for uvicorn
    run_e2e()
