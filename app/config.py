"""
Why this file exists:
The task guide requires "secure database configuration — no
hard-coded credentials". We NEVER write a password or connection
string directly in code. Instead we read it from an environment
variable, which python-dotenv loads from a local .env file (a
file that is git-ignored and never uploaded to GitHub).
"""

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"

    # Defaults to a local SQLite file if DATABASE_URL isn't set,
    # so the project runs with ZERO database setup. To use
    # PostgreSQL instead, just set DATABASE_URL in your .env, e.g.:
    #   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
    # No code changes needed — that's the whole point of an ORM.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(os.getcwd(), "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # turns off a feature we don't need
