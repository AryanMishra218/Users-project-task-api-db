from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    # unique=True makes the DATABASE ITSELF reject a duplicate
    # email, even if our Python code somehow forgot to check.
    # This is what "validation at the database/schema level" means.
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # A User can own many Projects, and can be assigned many Tasks.
    # backref="owner" / backref="assignee" means: from a Project
    # object you can do `project.owner.name`, and from a Task you
    # can do `task.assignee.name`, without writing extra queries.
    projects = db.relationship("Project", backref="owner", lazy=True)
    tasks_assigned = db.relationship(
        "Task", backref="assignee", lazy=True, foreign_keys="Task.assignee_id"
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}
