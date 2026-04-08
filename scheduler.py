"""
WUAN GARRY - Daily Scheduler
Runs as a background thread inside Render's single dyno.
Scrapes NLA results every 6 hours.
"""
import threading
import time
import logging
import os
from scraper import scrape_results, init_db, seed_db

logging.basicConfig(level=logging.INFO)
INTERVAL_SECONDS = 6 * 60 * 60   # 6 hours
DB_PATH = os.environ.get("DB_PATH", "lotto.db")

def run_scheduler():
    logging.info("Scheduler started – will scrape every %dh", INTERVAL_SECONDS // 3600)
    while True:
        try:
            n = scrape_results(DB_PATH)
            logging.info("Scheduled scrape done – %d new records", n)
        except Exception as e:
            logging.error("Scheduled scrape failed: %s", e)
        time.sleep(INTERVAL_SECONDS)

def start_scheduler():
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()

if __name__ == "__main__":
    init_db(DB_PATH)
    seed_db(DB_PATH)
    run_scheduler()
