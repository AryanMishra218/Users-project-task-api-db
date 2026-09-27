"""
Task endpoints:
  POST   /api/tasks               - create a task
  GET    /api/tasks               - list tasks (supports ?project_id= and ?status= filters)
  GET    /api/tasks/<id>          - get one task
  PUT    /api/tasks/<id>          - update task fields
  PATCH  /api/tasks/<id>/status   - update ONLY the status
  DELETE /api/tasks/<id>          - delete a task
"""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Task, Project, User
from app.errors import ApiError
from app.validators import require_fields, validate_choice, VALID_TASK_STATUSES, VALID_PRIORITIES

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["title", "project_id"])

    project_id = data["project_id"]
    if not Project.query.get(project_id):
        raise ApiError("project_id does not match any existing project.", 400)

    assignee_id = data.get("assignee_id")
    if assignee_id is not None and not User.query.get(assignee_id):
        raise ApiError("assignee_id does not match any existing user.", 400)

    priority = data.get("priority", "medium")
    validate_choice(priority, VALID_PRIORITIES, "priority")

    task = Task(
        title=data["title"].strip(),
        project_id=project_id,
        assignee_id=assignee_id,
        status="todo",
        priority=priority,
        due_date=data.get("due_date"),
    )
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    query = Task.query

    status_filter = request.args.get("status")
    if status_filter:
        query = query.filter_by(status=status_filter)

    project_filter = request.args.get("project_id", type=int)
    if project_filter is not None:
        query = query.filter_by(project_id=project_filter)

    tasks = query.order_by(Task.id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ApiError("Task not found.", 404)
    return jsonify(task.to_dict()), 200


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ApiError("Task not found.", 404)

    data = request.get_json(silent=True) or {}

    if "title" in data:
        if not str(data["title"]).strip():
            raise ApiError("title cannot be empty.", 400)
        task.title = data["title"].strip()

    if "priority" in data:
        validate_choice(data["priority"], VALID_PRIORITIES, "priority")
        task.priority = data["priority"]

    if "due_date" in data:
        task.due_date = data["due_date"]

    if "assignee_id" in data:
        assignee_id = data["assignee_id"]
        if assignee_id is not None and not User.query.get(assignee_id):
            raise ApiError("assignee_id does not match any existing user.", 400)
        task.assignee_id = assignee_id

    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route("/<int:task_id>/status", methods=["PATCH"])
def update_task_status(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ApiError("Task not found.", 404)

    data = request.get_json(silent=True) or {}
    require_fields(data, ["status"])
    validate_choice(data["status"], VALID_TASK_STATUSES, "status")

    task.status = data["status"]
    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ApiError("Task not found.", 404)
    db.session.delete(task)
    db.session.commit()
    return "", 204
