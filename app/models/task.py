from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates

VALID_STATUSES = ("todo", "in-progress", "done")
VALID_PRIORITIES = ("low", "medium", "high")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    # nullable=False means the DATABASE refuses to save a task
    # that isn't linked to a project — not just our Python code.
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    status = db.Column(db.String(20), nullable=False, default="todo")
    priority = db.Column(db.String(10), nullable=False, default="medium")
    due_date = db.Column(db.String(20), nullable=True)  # stored as "YYYY-MM-DD" text
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # CheckConstraint = a rule enforced BY THE DATABASE ITSELF.
    # Even if a bug in our Python code let an invalid status
    # through, the database would reject the write outright.
    # This is the deepest, most reliable layer of validation.
    __table_args__ = (
        CheckConstraint(status.in_(VALID_STATUSES), name="valid_status"),
        CheckConstraint(priority.in_(VALID_PRIORITIES), name="valid_priority"),
    )

    # @validates runs INSIDE Python, the moment the attribute is
    # set (e.g. task.status = "x"), before it ever reaches the
    # database. Having both this AND the CheckConstraint above is
    # "defense in depth" — two independent layers catching the
    # same mistake in different ways.
    @validates("status")
    def validate_status(self, key, value):
        if value not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {value}")
        return value

    @validates("priority")
    def validate_priority(self, key, value):
        if value not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {value}")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "project_id": self.project_id,
            "assignee_id": self.assignee_id,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
        }
