import json
import urllib.parse
import urllib.request
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
    # 1. Register a user (OWNER)
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    password = "password123"
    print(f"Using email: {email}")
    
    user_data = {
        "email": email,
        "full_name": "Test Owner",
        "password": password
    }
    status, body = make_request("POST", f"{BASE_URL}/auth/register", data=user_data)
    print_result("1. Register User (Owner)", status, body)
    
    if status not in [200, 201]:
        print("Registration failed. Stopping tests.")
        return

    # 2. Login to get token
    login_data = {
        "username": email,
        "password": password
    }
    status, body = make_request("POST", f"{BASE_URL}/auth/login", data=login_data, is_form=True)
    print_result("2. Login", status, body)
    if status != 200:
        return
        
    token = json.loads(body).get("access_token")
    owner_id = json.loads(body).get("user_id", 0) # Not in token response by default? Let's check token output.
    
    # 3. Create a workspace
    ws_data = {"name": "My New Workspace"}
    status, body = make_request("POST", f"{BASE_URL}/workspaces/", data=ws_data, token=token)
    print_result("3. Create Workspace", status, body)
    if status != 201:
        return
    ws_id = json.loads(body).get("id")
    
    # 4. Get workspace
    status, body = make_request("GET", f"{BASE_URL}/workspaces/{ws_id}", token=token)
    print_result("4. Get Workspace", status, body)
    
    # 5. Register a second user (MEMBER) to add to workspace
    member_email = f"member_{uuid.uuid4().hex[:6]}@example.com"
    member_data = {
        "email": member_email,
        "full_name": "Test Member",
        "password": password
    }
    status, member_body = make_request("POST", f"{BASE_URL}/auth/register", data=member_data)
    print_result("5. Register Second User (Member)", status, member_body)
    member_id = json.loads(member_body).get("id")
    
    # 6. Add member to workspace
    add_member_data = {
        "user_id": member_id,
        "role": "EDITOR"
    }
    status, body = make_request("POST", f"{BASE_URL}/workspaces/{ws_id}/members", data=add_member_data, token=token)
    print_result("6. Add Member to Workspace", status, body)
    
    # 7. Create project in workspace
    proj_data = {
        "name": "My First Project",
        "description": "Project Description"
    }
    status, body = make_request("POST", f"{BASE_URL}/workspaces/{ws_id}/projects", data=proj_data, token=token)
    print_result("7. Create Project in Workspace", status, body)
    
    # 8. Remove member from workspace
    status, body = make_request("DELETE", f"{BASE_URL}/workspaces/{ws_id}/members/{member_id}", token=token)
    print_result("8. Remove Member from Workspace", status, body)

if __name__ == "__main__":
    run_tests()
