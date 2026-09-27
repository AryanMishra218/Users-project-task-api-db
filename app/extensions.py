"""
Why this file exists on its own (not inside __init__.py):
The `db` object needs to be imported by our model files AND by
app/__init__.py. If we created `db` inside __init__.py, importing
it from models.py would create a "circular import" (A needs B,
B needs A) — a classic Python trap. Keeping it in its own tiny
file lets everyone import it safely.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
