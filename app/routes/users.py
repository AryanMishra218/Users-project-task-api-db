"""
User management endpoints:
  POST   /api/users        - create a user
  GET    /api/users        - list all users
  GET    /api/users/<id>   - get one user
  DELETE /api/users/<id>   - delete a user

Compare this file to Task 2's version: the ROUTES look almost
identical. What changed is WHERE the data lives — `store.users`
(a Python dict) became `User.query` (a real SQL query) and
`db.session.add/commit` (a real database write). The route
functions barely had to change.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User
from app.errors import ApiError
from app.validators import require_fields, validate_email

users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name", "email"])
    validate_email(data["email"])

    email = data["email"].strip()

    # Application-level duplicate check (gives a clean error message).
    if User.query.filter_by(email=email).first():
        raise ApiError("A user with this email already exists.", 409)

    user = User(name=data["name"].strip(), email=email)
    db.session.add(user)
    db.session.commit()  # this is the moment it's actually saved to disk

    return jsonify(user.to_dict()), 201


@users_bp.route("", methods=["GET"])
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify([u.to_dict() for u in users]), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ApiError("User not found.", 404)
    return jsonify(user.to_dict()), 200


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ApiError("User not found.", 404)
    db.session.delete(user)
    db.session.commit()
    return "", 204
