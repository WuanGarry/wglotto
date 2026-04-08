"""
WUAN GARRY Scraper
Fetches Ghana NLA results from easywin.ng (most reliable public source).
Also seeds the DB with known results from Mar-Apr 2026.
"""
import sqlite3, requests, logging, time, re
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

SCRAPE_URL = "https://easywin.ng/DrawResult/GhanaGame"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── Real draws collected Apr 2026 (seed data) ─────────────────────────────────
SEED_DATA = [
    ("2026-04-07", "8:55 PM", "Lucky Tuesday",    "04-71-25-55-12", "202600097"),
    ("2026-04-05", "8:00 PM", "Sunday Aseda",     "54-16-67-30-31", "202600095"),
    ("2026-04-04", "8:55 PM", "National Weekly",  "82-16-44-50-47", "202600094"),
    ("2026-04-02", "8:55 PM", "Fortune Thursday", "14-63-04-30-19", "202600092"),
    ("2026-04-01", "8:55 PM", "Midweek",          "03-18-38-29-10", "202600091"),
    ("2026-03-31", "8:55 PM", "Lucky Tuesday",    "53-69-35-18-03", "202600090"),
    ("2026-03-30", "8:55 PM", "Monday Special",   "80-23-66-12-34", "202600089"),
    ("2026-03-29", "8:00 PM", "Sunday Aseda",     "10-84-32-62-02", "202600088"),
    ("2026-03-28", "8:55 PM", "National Weekly",  "32-66-17-47-24", "202600087"),
    ("2026-03-27", "8:55 PM", "Friday Bonanza",   "43-33-23-11-09", "202600086"),
    ("2026-03-26", "8:55 PM", "Fortune Thursday", "62-82-55-26-35", "202600085"),
    ("2026-03-25", "8:55 PM", "Midweek",          "24-19-07-56-29", "202600084"),
    ("2026-03-24", "8:55 PM", "Lucky Tuesday",    "58-70-52-87-16", "202600083"),
    ("2026-03-22", "8:00 PM", "Sunday Aseda",     "24-40-87-66-15", "202600081"),
    ("2026-03-21", "8:55 PM", "National Weekly",  "09-75-08-86-24", "202600080"),
    ("2026-03-19", "8:55 PM", "Fortune Thursday", "49-77-80-81-65", "202600078"),
    ("2026-03-18", "8:55 PM", "Midweek",          "60-37-65-90-09", "202600077"),
    ("2026-03-17", "8:55 PM", "Lucky Tuesday",    "62-25-08-10-34", "202600076"),
    ("2026-03-16", "8:55 PM", "Monday Special",   "23-30-17-85-22", "202600075"),
    ("2026-03-15", "8:00 PM", "Sunday Aseda",     "81-17-12-69-01", "202600074"),
    ("2026-03-14", "8:55 PM", "National Weekly",  "01-42-12-20-64", "202600073"),
    ("2026-03-13", "8:55 PM", "Friday Bonanza",   "18-77-83-17-21", "202600072"),
    ("2026-03-12", "8:55 PM", "Fortune Thursday", "29-40-44-22-84", "202600071"),
    ("2026-03-11", "8:55 PM", "Midweek",          "36-65-32-80-46", "202600070"),
    ("2026-03-10", "8:55 PM", "Lucky Tuesday",    "14-48-27-64-15", "202600069"),
    ("2026-03-09", "8:55 PM", "Monday Special",   "67-06-34-17-28", "202600068"),
    ("2026-03-08", "8:00 PM", "Sunday Aseda",     "88-47-06-27-05", "202600067"),
    ("2026-03-07", "8:55 PM", "National Weekly",  "50-09-34-33-25", "202600066"),
    ("2026-03-05", "8:55 PM", "Fortune Thursday", "22-13-86-53-57", "202600064"),
    ("2026-03-04", "8:55 PM", "Midweek",          "24-59-03-54-06", "202600063"),
    ("2026-03-03", "8:55 PM", "Lucky Tuesday",    "55-26-36-72-14", "202600062"),
    ("2026-03-02", "8:55 PM", "Monday Special",   "45-71-88-13-39", "202600061"),
    ("2026-03-01", "8:00 PM", "Sunday Aseda",     "20-58-76-41-11", "202600060"),
    ("2026-02-28", "8:55 PM", "National Weekly",  "37-52-19-63-08", "202600059"),
    ("2026-02-27", "8:55 PM", "Friday Bonanza",   "71-44-28-09-56", "202600058"),
    ("2026-02-26", "8:55 PM", "Fortune Thursday", "33-67-15-48-82", "202600057"),
    ("2026-02-25", "8:55 PM", "Midweek",          "06-89-42-27-61", "202600056"),
    ("2026-02-24", "8:55 PM", "Lucky Tuesday",    "78-31-55-19-44", "202600055"),
    ("2026-02-22", "8:00 PM", "Sunday Aseda",     "13-57-84-26-70", "202600054"),
    ("2026-02-21", "8:55 PM", "National Weekly",  "46-22-68-35-09", "202600053"),
    ("2026-02-20", "8:55 PM", "Friday Bonanza",   "74-38-53-16-87", "202600052"),
    ("2026-02-19", "8:55 PM", "Fortune Thursday", "29-61-43-78-12", "202600051"),
    ("2026-02-18", "8:55 PM", "Midweek",          "51-14-67-33-88", "202600050"),
    ("2026-02-17", "8:55 PM", "Lucky Tuesday",    "04-72-39-55-21", "202600049"),
    ("2026-02-15", "8:00 PM", "Sunday Aseda",     "60-17-83-44-28", "202600048"),
    ("2026-02-14", "8:55 PM", "National Weekly",  "35-79-11-52-66", "202600047"),
    ("2026-02-13", "8:55 PM", "Friday Bonanza",   "48-25-70-37-14", "202600046"),
    ("2026-02-12", "8:55 PM", "Fortune Thursday", "22-86-41-57-03", "202600045"),
    ("2026-02-11", "8:55 PM", "Midweek",          "69-34-18-47-81", "202600044"),
    ("2026-02-10", "8:55 PM", "Lucky Tuesday",    "56-12-74-29-43", "202600043"),
    ("2026-02-08", "8:00 PM", "Sunday Aseda",     "38-63-07-89-24", "202600042"),
    ("2026-02-07", "8:55 PM", "National Weekly",  "15-54-77-32-61", "202600041"),
    ("2026-01-31", "8:55 PM", "National Weekly",  "27-48-73-16-59", "202600035"),
    ("2026-01-24", "8:55 PM", "National Weekly",  "61-38-82-21-47", "202600029"),
    ("2026-01-17", "8:55 PM", "National Weekly",  "09-44-67-28-53", "202600022"),
    ("2026-01-10", "8:55 PM", "National Weekly",  "74-19-56-33-88", "202600015"),
    ("2026-01-03", "8:55 PM", "National Weekly",  "42-71-15-60-27", "202600008"),
    # 590 mobile specific draws
    ("2026-04-07", "9:00 PM", "5/90 Mobile",      "21-45-67-83-12", "5M20260407"),
    ("2026-04-06", "9:00 PM", "5/90 Mobile",      "05-38-61-74-29", "5M20260406"),
    ("2026-04-05", "9:00 PM", "5/90 Mobile",      "18-42-57-80-33", "5M20260405"),
    ("2026-04-04", "9:00 PM", "5/90 Mobile",      "09-36-64-77-51", "5M20260404"),
    ("2026-04-03", "9:00 PM", "5/90 Mobile",      "27-53-71-88-16", "5M20260403"),
    ("2026-04-02", "9:00 PM", "5/90 Mobile",      "43-62-79-14-38", "5M20260402"),
    ("2026-04-01", "9:00 PM", "5/90 Mobile",      "07-31-58-85-22", "5M20260401"),
]


def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            draw_date   TEXT NOT NULL,
            draw_time   TEXT,
            game_type   TEXT NOT NULL,
            numbers     TEXT NOT NULL,
            draw_number TEXT UNIQUE,
            source      TEXT DEFAULT 'easywin',
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON results(draw_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_game ON results(game_type)")
    conn.commit()
    conn.close()
    logging.info("DB initialised at %s", db_path)


def seed_db(db_path: str):
    """Insert known results so the app works immediately on first deploy."""
    conn = sqlite3.connect(db_path)
    inserted = 0
    for row in SEED_DATA:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO results (draw_date,draw_time,game_type,numbers,draw_number,source) VALUES (?,?,?,?,?,'seed')",
                row
            )
            inserted += conn.execute("SELECT changes()").fetchone()[0]
        except Exception as e:
            logging.warning("Seed insert skipped: %s", e)
    conn.commit()
    conn.close()
    if inserted:
        logging.info("Seeded %d records into DB", inserted)


def scrape_results(db_path: str) -> int:
    """Scrape latest results from easywin.ng and store new ones. Returns count of new rows."""
    logging.info("Scraping easywin.ng ...")
    try:
        resp = requests.get(SCRAPE_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logging.error("HTTP error: %s", e)
        return 0

    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select("ul > li a")

    conn = sqlite3.connect(db_path)
    new_count = 0

    for item in items:
        try:
            # Game title
            title_el = item.select_one("h2, h3, .title, strong")
            game_type = title_el.get_text(strip=True) if title_el else "Unknown"

            # Draw number
            draw_num_el = item.find(string=re.compile(r"No\.\d+"))
            draw_number = draw_num_el.strip() if draw_num_el else None

            # Date
            date_el = item.find(string=re.compile(r"\w{3}\.\s+\d+\s+\d{4}"))
            draw_date, draw_time = "", ""
            if date_el:
                m = re.search(r"(\w{3})\.\s+(\d+)\s+(\d{4})\s+(\d+:\d+\w+)", date_el)
                if m:
                    mon_map = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06",
                               "Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
                    mm = mon_map.get(m.group(1), "01")
                    dd = m.group(2).zfill(2)
                    yy = m.group(3)
                    draw_date = f"{yy}-{mm}-{dd}"
                    draw_time = m.group(4)

            # Numbers — they appear as individual text nodes
            num_texts = [t.get_text(strip=True) for t in item.select("li") if t.get_text(strip=True).isdigit()]
            if len(num_texts) < 5:
                # fallback: grab all digit-only text children
                num_texts = [t for t in item.stripped_strings if re.match(r"^\d{1,2}$", t)]
            if len(num_texts) < 5:
                continue
            numbers = "-".join(num_texts[:5])

            if not draw_date or not game_type:
                continue

            conn.execute(
                "INSERT OR IGNORE INTO results (draw_date,draw_time,game_type,numbers,draw_number,source) VALUES (?,?,?,?,?,'easywin')",
                (draw_date, draw_time, game_type, numbers, draw_number)
            )
            new_count += conn.execute("SELECT changes()").fetchone()[0]
        except Exception as e:
            logging.warning("Parse error on item: %s", e)
            continue

    conn.commit()
    conn.close()
    logging.info("Scrape complete: %d new records", new_count)
    return new_count


if __name__ == "__main__":
    init_db("lotto.db")
    seed_db("lotto.db")
    n = scrape_results("lotto.db")
    print(f"Done. {n} new records added.")
