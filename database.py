import json
import os
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


FIREBASE_DATABASE_URL = os.environ.get(
    "FIREBASE_DATABASE_URL",
    "https://project-kissan-48284-default-rtdb.asia-southeast1.firebasedatabase.app",
).rstrip("/")


def _firebase_request(method, path, payload=None, id_token=None):
    query = urlencode({"auth": id_token}) if id_token else ""
    url = f"{FIREBASE_DATABASE_URL}/{path}.json"
    if query:
        url = f"{url}?{query}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            data = response.read()
            return json.loads(data) if data else None
    except (HTTPError, URLError) as error:
        raise RuntimeError("Firebase Realtime Database request failed") from error


def initialize_database():
    # Firebase creates the task collection on the first successful write.
    return None


def create_task(task, prediction, id_token):
    task_data = {
        "userId": task.user_id,
        "task_name": task.task_name,
        "priority": task.priority,
        "deadline": task.deadline.isoformat(),
        "status": task.status,
        "category": task.category,
        "estimated_time": task.estimated_time,
        "priority_score": prediction["priority_score"],
        "predicted_priority": prediction["predicted_priority"],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    result = _firebase_request("POST", f"users/{quote(task.user_id, safe='')}/tasks", task_data, id_token)
    task_id = result.get("name") if result else None
    return get_task(task_id, task.user_id, id_token)


def get_task(task_id, user_id, id_token):
    if not task_id:
        return None
    task = _firebase_request("GET", f"users/{quote(user_id, safe='')}/tasks/{quote(str(task_id), safe='')}", id_token=id_token)
    if not task:
        return None
    task["id"] = task_id
    task["user_id"] = task.pop("userId", user_id)
    return task


def list_tasks(user_id, id_token):
    result = _firebase_request("GET", f"users/{quote(user_id, safe='')}/tasks", id_token=id_token) or {}
    tasks = []
    for task_id, task in result.items():
        legacy_deadline = task.get("dueDate", "")[:10] or date.today().isoformat()
        task = {
            **task,
            "task_name": task.get("task_name") or task.get("title") or task.get("text") or "Untitled task",
            "priority": task.get("priority") or "Medium",
            "deadline": task.get("deadline") or legacy_deadline,
            "status": task.get("status") or ("Completed" if task.get("completed") else "Pending"),
            "category": task.get("category") or "General",
            "estimated_time": task.get("estimated_time") or 1,
            "priority_score": task.get("priority_score") if task.get("priority_score") is not None else 0.5,
            "predicted_priority": task.get("predicted_priority") or task.get("priority") or "Medium",
            "created_at": task.get("created_at") or task.get("createdAt") or datetime.utcnow().isoformat() + "Z",
        }
        task["id"] = task_id
        task["user_id"] = task.pop("userId", user_id)
        tasks.append(task)
    priority_order = {"High": 2, "Medium": 1, "Low": 0}
    return sorted(
        tasks,
        key=lambda task: (
            float(task.get("priority_score", 0)),
            priority_order.get(task.get("priority"), -1),
            task.get("deadline", ""),
        ),
        reverse=True,
    )


def delete_task(task_id, user_id, id_token):
    existing = get_task(task_id, user_id, id_token)
    if not existing:
        return False
    _firebase_request("DELETE", f"users/{quote(user_id, safe='')}/tasks/{quote(str(task_id), safe='')}", id_token=id_token)
    return True


def update_task_status(task_id, user_id, status, id_token):
    existing = get_task(task_id, user_id, id_token)
    if not existing:
        return False
    _firebase_request("PATCH", f"users/{quote(user_id, safe='')}/tasks/{quote(str(task_id), safe='')}", {"status": status}, id_token)
    return True
