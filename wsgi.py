"""
wsgi.py — entry point for gunicorn on Render
Starts background scheduler + serves Flask app.
"""
import os
from app import app
from scraper import init_db, seed_db
from scheduler import start_scheduler

DB_PATH = os.environ.get("DB_PATH", "lotto.db")

# Initialise DB and seed on startup
init_db(DB_PATH)
seed_db(DB_PATH)

# Start background scraper thread
start_scheduler()

if __name__ == "__main__":
    app.run()
