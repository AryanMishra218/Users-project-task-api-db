"""
Project endpoints:
  POST   /api/projects        - create a project
  GET    /api/projects        - list all projects
  GET    /api/projects/<id>   - get one project (with task stats)
"""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Project, User
from app.errors import ApiError
from app.validators import require_fields

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("", methods=["POST"])
def create_project():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name"])

    owner_id = data.get("owner_id")
    if owner_id is not None and not User.query.get(owner_id):
        raise ApiError("owner_id does not match any existing user.", 400)

    project = Project(
        name=data["name"].strip(),
        description=data.get("description", "").strip(),
        owner_id=owner_id,
    )
    db.session.add(project)
    db.session.commit()

    return jsonify(project.to_dict()), 201


@projects_bp.route("", methods=["GET"])
def list_projects():
    projects = Project.query.order_by(Project.id).all()
    return jsonify([p.to_dict() for p in projects]), 200


@projects_bp.route("/<int:project_id>", methods=["GET"])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        raise ApiError("Project not found.", 404)

    # project.tasks works because of the `relationship()` we
    # defined in the Task model — SQLAlchemy runs the JOIN query
    # for us automatically the first time we access it.
    result = project.to_dict()
    result["task_count"] = len(project.tasks)
    result["tasks_done"] = sum(1 for t in project.tasks if t.status == "done")
    return jsonify(result), 200
