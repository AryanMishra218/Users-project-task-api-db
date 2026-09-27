# Importing the models here means: as soon as someone does
# `from app import models` (or, indirectly, `from app import
# create_app`), all three models get registered with
# SQLAlchemy. Without this, db.create_all() wouldn't know
# these tables exist.
from app.models.user import User
from app.models.project import Project
from app.models.task import Task

__all__ = ["User", "Project", "Task"]
