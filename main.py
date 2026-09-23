"""
Legacy entry point for backward compatibility.
The main application is now in app/main.py
"""

from app.main import app

__all__ = ["app"]
