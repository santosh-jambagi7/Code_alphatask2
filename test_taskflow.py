import sys
import asyncio
from fastapi.testclient import TestClient
from taskflow.backend.app import app
from taskflow.backend.database import init_db, get_db

def test_full_system():
    print("[1] Initializing database...")
    init_db()

    client = TestClient(app)

    # 1. Test Login with Alice
    print("[2] Testing user authentication (Alice)...")
    res = client.post("/api/auth/login", json={"username_or_email": "alice", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    alice_data = res.json()
    alice_token = alice_data["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    print(f"    Alice logged in successfully: {alice_data['user']['full_name']}")

    # 2. Test Login with Bob
    print("[3] Testing user authentication (Bob)...")
    res = client.post("/api/auth/login", json={"username_or_email": "bob", "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    bob_data = res.json()
    bob_token = bob_data["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}
    print(f"    Bob logged in successfully: {bob_data['user']['full_name']}")

    # 3. Test Register New User
    print("[4] Testing new user registration...")
    new_user_payload = {
        "username": "evan",
        "email": "evan@example.com",
        "password": "securepassword123",
        "full_name": "Evan Wright",
        "avatar_color": "#8b5cf6",
        "title": "DevOps Engineer"
    }
    res = client.post("/api/auth/register", json=new_user_payload)
    assert res.status_code in [200, 400], f"Register failed: {res.text}"
    if res.status_code == 200:
        print("    Registered new user: Evan Wright")

    # 4. List Projects
    print("[5] Testing listing projects for Alice...")
    res = client.get("/api/projects", headers=alice_headers)
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) > 0, "No projects returned"
    print(f"    Found {len(projects)} projects. First: {projects[0]['name']}")
    proj_id = projects[0]["id"]

    # 5. Create a New Group Project
    print("[6] Testing create new group project...")
    new_proj_payload = {
        "name": "Cloud Infrastructure Migration",
        "description": "Migrate services to Kubernetes with zero downtime",
        "color": "#10b981",
        "icon": "☁️"
    }
    res = client.post("/api/projects", json=new_proj_payload, headers=alice_headers)
    assert res.status_code == 200, f"Create project failed: {res.text}"
    created_proj = res.json()
    new_proj_id = created_proj["id"]
    print(f"    Created project ID {new_proj_id}: {created_proj['name']}")

    # 6. Add Bob to New Project
    print("[7] Testing inviting member to project...")
    res = client.post(f"/api/projects/{new_proj_id}/members", json={"username_or_email": "bob", "role": "admin"}, headers=alice_headers)
    assert res.status_code == 200, f"Add member failed: {res.text}"
    members = res.json()
    assert any(m["username"] == "bob" for m in members), "Bob was not added to members"
    print(f"    Successfully added Bob as admin. Member count: {len(members)}")

    # 7. Add Column to Project
    print("[8] Testing column creation...")
    res = client.post(f"/api/projects/{new_proj_id}/columns", json={"title": "Testing / QA", "color": "#f59e0b"}, headers=alice_headers)
    assert res.status_code == 200
    qa_col = res.json()
    print(f"    Added column: {qa_col['title']} (ID: {qa_col['id']})")

    # 8. Create Task in New Project and Assign Bob
    print("[9] Testing task creation with assignees and labels...")
    first_col_id = created_proj["columns"][0]["id"]
    task_payload = {
        "column_id": first_col_id,
        "title": "Setup Terraform EKS Cluster",
        "description": "Configure multi-az Kubernetes cluster with autoscaling group",
        "priority": "urgent",
        "due_date": "2026-10-15",
        "assignee_ids": [bob_data["user"]["id"]],
        "labels": [{"name": "DevOps", "color": "#10b981"}, {"name": "Infra", "color": "#3b82f6"}]
    }
    res = client.post(f"/api/projects/{new_proj_id}/tasks", json=task_payload, headers=alice_headers)
    assert res.status_code == 200, f"Create task failed: {res.text}"
    task = res.json()
    task_id = task["id"]
    print(f"    Created task ID {task_id}: '{task['title']}', Priority: {task['priority']}")
    assert len(task["assignees"]) == 1
    assert task["assignees"][0]["username"] == "bob"

    # 9. Verify Bob received a notification for assignment
    print("[10] Testing notification delivery for assigned user...")
    res = client.get("/api/notifications", headers=bob_headers)
    assert res.status_code == 200
    notifs_data = res.json()
    assert notifs_data["unread_count"] > 0
    print(f"    Bob has {notifs_data['unread_count']} unread notifications. Latest: {notifs_data['notifications'][0]['message']}")

    # 10. Test Move Task (Drag-and-Drop)
    print("[11] Testing moving task to QA column...")
    res = client.post(f"/api/tasks/{task_id}/move", json={"target_column_id": qa_col["id"], "target_position": 0}, headers=bob_headers)
    assert res.status_code == 200
    moved_task = res.json()
    assert moved_task["column_id"] == qa_col["id"]
    print(f"    Task successfully moved to column ID {qa_col['id']}")

    # 11. Test Subtask Creation & Toggle
    print("[12] Testing subtask checklist creation and toggle...")
    res = client.post(f"/api/tasks/{task_id}/subtasks", json={"title": "Provision VPC and Subnets"}, headers=bob_headers)
    assert res.status_code == 200
    subtask = res.json()
    sub_id = subtask["id"]
    print(f"    Added subtask ID {sub_id}: '{subtask['title']}'")

    res = client.put(f"/api/subtasks/{sub_id}/toggle", headers=bob_headers)
    assert res.status_code == 200
    toggled = res.json()
    assert toggled["is_completed"] is True
    print("    Toggled subtask completion to TRUE")

    # 12. Test Comments & Activity Log
    print("[13] Testing task commenting...")
    res = client.post(f"/api/tasks/{task_id}/comments", json={"content": "VPC configured and CIDR blocks mapped."}, headers=bob_headers)
    assert res.status_code == 200
    comment = res.json()
    print(f"    Bob commented: \"{comment['content']}\"")

    res = client.get(f"/api/tasks/{task_id}/comments", headers=alice_headers)
    assert res.status_code == 200
    comments = res.json()
    assert len(comments) >= 1

    # Check project activity logs
    print("[14] Testing project activity audit log...")
    res = client.get(f"/api/projects/{new_proj_id}/activity", headers=alice_headers)
    assert res.status_code == 200
    activity = res.json()
    assert len(activity) > 0
    print(f"    Found {len(activity)} activity log events. Latest: {activity[0]['details']}")

    # 13. Test WebSocket connection
    print("[15] Testing WebSocket real-time connection...")
    with client.websocket_connect(f"/ws/projects/{new_proj_id}?token={alice_token}") as ws_alice:
        # Alice sends ping
        ws_alice.send_json({"type": "PING"})
        resp = ws_alice.receive_json()
        assert resp["type"] in ["PRESENCE_UPDATE", "PONG"], f"Unexpected WS response: {resp}"
        print(f"    WebSocket connected and received: {resp['type']}")

    print("\n============================================================")
    print("SUCCESS: ALL TASKFLOW INTEGRATION TESTS PASSED PERFECTLY!")
    print("============================================================\n")

if __name__ == "__main__":
    test_full_system()
