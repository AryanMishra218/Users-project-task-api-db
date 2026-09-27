from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")

    # ForeignKey creates a real, enforced link to users.id at the
    # database level. If you tried to insert a project with an
    # owner_id that doesn't exist, the database itself would
    # refuse it (a "foreign key constraint" violation) — this is
    # a second, deeper layer of validation beyond our Python checks.
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # A Project has many Tasks. cascade="all, delete-orphan" means:
    # if a Project is deleted, its Tasks are automatically deleted
    # too — the database won't be left with "orphaned" tasks
    # pointing at a project that no longer exists.
    tasks = db.relationship(
        "Task", backref="project", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
        }
