import urllib.request
import urllib.parse
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_result(step, status, body):
    print(f"--- {step} ---")
    print(f"Status: {status}")
    try:
        parsed = json.loads(body)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except:
        print(body)
    print("\n")

def make_request(method, url, data=None, token=None, is_form=False):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = None
    if data is not None:
        if is_form:
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")
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
    # 1. Setup: Register & Login
    email = f"tasktest_{uuid.uuid4().hex[:6]}@example.com"
    password = "password123"
    print(f"Setting up with email: {email}")
    
    make_request("POST", f"{BASE_URL}/auth/register", data={"email": email, "full_name": "Test User", "password": password})
    status, body = make_request("POST", f"{BASE_URL}/auth/login", data={"username": email, "password": password}, is_form=True)
    if status != 200:
        print("Login failed.", body)
        return
    token = json.loads(body).get("access_token")
    
    # 2. Setup: Create Workspace & Project
    status, ws_body = make_request("POST", f"{BASE_URL}/workspaces/", data={"name": "Task Test WS"}, token=token)
    ws_id = json.loads(ws_body).get("id")
    status, proj_body = make_request("POST", f"{BASE_URL}/workspaces/{ws_id}/projects", data={"name": "Task Test Project"}, token=token)
    proj_id = json.loads(proj_body).get("id")
    print(f"Created Workspace ID: {ws_id}, Project ID: {proj_id}\n")

    # 3. Create Multiple Tasks
    tasks_to_create = [
        {"title": "Task 1", "status": "TODO", "priority": "HIGH"},
        {"title": "Task 2", "status": "IN_PROGRESS", "priority": "MEDIUM"},
        {"title": "Task 3", "status": "TODO", "priority": "LOW"},
        {"title": "Task 4", "status": "DONE", "priority": "HIGH"},
        {"title": "Task 5", "status": "IN_PROGRESS", "priority": "URGENT"},
    ]
    
    print("--- 1. Creating 5 Tasks ---")
    for t in tasks_to_create:
        status, body = make_request("POST", f"{BASE_URL}/projects/{proj_id}/tasks", data=t, token=token)
        print(f"Created '{t['title']}' - Status: {status}")
    print("\n")

    # 4. Get all tasks (No filters, limit 20)
    status, body = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks", token=token)
    print_result("2. Get All Tasks (No filters)", status, body)

    # 5. Filter by status=TODO
    status, body = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks?status=TODO", token=token)
    print_result("3. Filter by Status = 'TODO'", status, body)

    # 6. Filter by priority=HIGH
    status, body = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks?priority=HIGH", token=token)
    print_result("4. Filter by Priority = 'HIGH'", status, body)

    # 7. Pagination: skip=1, limit=2
    status, body = make_request("GET", f"{BASE_URL}/projects/{proj_id}/tasks?skip=1&limit=2", token=token)
    print_result("5. Pagination (skip=1, limit=2)", status, body)

    # 8. Update a task
    # Let's get the ID of the first task from previous request
    tasks = json.loads(body)
    if tasks:
        task_id = tasks[0]["id"]
        status, body = make_request("PATCH", f"{BASE_URL}/tasks/{task_id}", data={"status": "DONE", "priority": "URGENT"}, token=token)
        print_result(f"6. Update Task {task_id} to DONE/URGENT", status, body)
    
if __name__ == "__main__":
    run_tests()
