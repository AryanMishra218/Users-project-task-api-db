"""
The "application factory" pattern: instead of creating the Flask
app as a bare global variable, we wrap creation in a function.
This is the professional standard because it lets us create
multiple instances of the app with different configs (e.g. one
for running the real server, a separate one for automated tests)
without them interfering with each other.
"""

from flask import Flask, jsonify
from app.config import Config
from app.errors import ApiError
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Connect SQLAlchemy to this Flask app.
    db.init_app(app)

    # Importing models here (via app.models) registers all three
    # tables with SQLAlchemy BEFORE we call create_all() below.
    from app import models  # noqa: F401

    with app.app_context():
        # create_all() looks at every registered model and creates
        # any tables that don't exist yet. It never touches tables
        # that already exist, so it's safe to run every startup.
        # (For real production apps with evolving schemas, teams
        # use a tool called "Flask-Migrate" instead — worth learning
        # next, but create_all() is the right starting point here.)
        db.create_all()

    # ---- Register route groups (blueprints) ----
    from app.routes.users import users_bp
    from app.routes.projects import projects_bp
    from app.routes.tasks import tasks_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

    # ---- Centralized error handling ----
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({"error": "Method not allowed on this endpoint."}), 405

    @app.errorhandler(500)
    def handle_500(error):
        db.session.rollback()  # undo any half-finished DB changes
        return jsonify({"error": "Internal server error."}), 500

    @app.route("/")
    def index():
        return jsonify(
            {
                "service": "Users, Projects & Tasks API",
                "status": "running",
                "database": app.config["SQLALCHEMY_DATABASE_URI"].split("://")[0],
                "docs": "See README.md for all endpoints.",
            }
        )

    return app
