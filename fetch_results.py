"""
fetch_results.py
================
Scrapes https://www.nla.com.gh/winning-numbers using Playwright,
merges with existing data/results.json, and writes the updated file.

Run by GitHub Actions every day at 10 PM Ghana time.
Also runnable locally:  python fetch_results.py
"""

import json, os, re, time, logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

NLA_URL   = "https://www.nla.com.gh/winning-numbers"
DATA_FILE = Path("data/results.json")

# ── Seed: verified real draws (fallback if scrape fails) ──────────────────────
SEED = [
    {"draw_date":"2026-04-07","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"04-71-25-55-12","draw_number":"202600097","source":"nla.com.gh"},
    {"draw_date":"2026-04-05","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"54-16-67-30-31","draw_number":"202600095","source":"nla.com.gh"},
    {"draw_date":"2026-04-04","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"82-16-44-50-47","draw_number":"202600094","source":"nla.com.gh"},
    {"draw_date":"2026-04-02","draw_time":"8:55 PM","game_type":"Fortune Thursday", "numbers":"14-63-04-30-19","draw_number":"202600092","source":"nla.com.gh"},
    {"draw_date":"2026-04-01","draw_time":"8:55 PM","game_type":"Midweek",          "numbers":"03-18-38-29-10","draw_number":"202600091","source":"nla.com.gh"},
    {"draw_date":"2026-03-31","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"53-69-35-18-03","draw_number":"202600090","source":"nla.com.gh"},
    {"draw_date":"2026-03-30","draw_time":"8:55 PM","game_type":"Monday Special",   "numbers":"80-23-66-12-34","draw_number":"202600089","source":"nla.com.gh"},
    {"draw_date":"2026-03-29","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"10-84-32-62-02","draw_number":"202600088","source":"nla.com.gh"},
    {"draw_date":"2026-03-28","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"32-66-17-47-24","draw_number":"202600087","source":"nla.com.gh"},
    {"draw_date":"2026-03-27","draw_time":"8:55 PM","game_type":"Friday Bonanza",   "numbers":"43-33-23-11-09","draw_number":"202600086","source":"nla.com.gh"},
    {"draw_date":"2026-03-26","draw_time":"8:55 PM","game_type":"Fortune Thursday", "numbers":"62-82-55-26-35","draw_number":"202600085","source":"nla.com.gh"},
    {"draw_date":"2026-03-25","draw_time":"8:55 PM","game_type":"Midweek",          "numbers":"24-19-07-56-29","draw_number":"202600084","source":"nla.com.gh"},
    {"draw_date":"2026-03-24","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"58-70-52-87-16","draw_number":"202600083","source":"nla.com.gh"},
    {"draw_date":"2026-03-22","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"24-40-87-66-15","draw_number":"202600081","source":"nla.com.gh"},
    {"draw_date":"2026-03-21","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"09-75-08-86-24","draw_number":"202600080","source":"nla.com.gh"},
    {"draw_date":"2026-03-19","draw_time":"8:55 PM","game_type":"Fortune Thursday", "numbers":"49-77-80-81-65","draw_number":"202600078","source":"nla.com.gh"},
    {"draw_date":"2026-03-18","draw_time":"8:55 PM","game_type":"Midweek",          "numbers":"60-37-65-90-09","draw_number":"202600077","source":"nla.com.gh"},
    {"draw_date":"2026-03-17","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"62-25-08-10-34","draw_number":"202600076","source":"nla.com.gh"},
    {"draw_date":"2026-03-16","draw_time":"8:55 PM","game_type":"Monday Special",   "numbers":"23-30-17-85-22","draw_number":"202600075","source":"nla.com.gh"},
    {"draw_date":"2026-03-15","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"81-17-12-69-01","draw_number":"202600074","source":"nla.com.gh"},
    {"draw_date":"2026-03-14","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"01-42-12-20-64","draw_number":"202600073","source":"nla.com.gh"},
    {"draw_date":"2026-03-13","draw_time":"8:55 PM","game_type":"Friday Bonanza",   "numbers":"18-77-83-17-21","draw_number":"202600072","source":"nla.com.gh"},
    {"draw_date":"2026-03-12","draw_time":"8:55 PM","game_type":"Fortune Thursday", "numbers":"29-40-44-22-84","draw_number":"202600071","source":"nla.com.gh"},
    {"draw_date":"2026-03-11","draw_time":"8:55 PM","game_type":"Midweek",          "numbers":"36-65-32-80-46","draw_number":"202600070","source":"nla.com.gh"},
    {"draw_date":"2026-03-10","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"14-48-27-64-15","draw_number":"202600069","source":"nla.com.gh"},
    {"draw_date":"2026-03-09","draw_time":"8:55 PM","game_type":"Monday Special",   "numbers":"67-06-34-17-28","draw_number":"202600068","source":"nla.com.gh"},
    {"draw_date":"2026-03-08","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"88-47-06-27-05","draw_number":"202600067","source":"nla.com.gh"},
    {"draw_date":"2026-03-07","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"50-09-34-33-25","draw_number":"202600066","source":"nla.com.gh"},
    {"draw_date":"2026-03-05","draw_time":"8:55 PM","game_type":"Fortune Thursday", "numbers":"22-13-86-53-57","draw_number":"202600064","source":"nla.com.gh"},
    {"draw_date":"2026-03-04","draw_time":"8:55 PM","game_type":"Midweek",          "numbers":"24-59-03-54-06","draw_number":"202600063","source":"nla.com.gh"},
    {"draw_date":"2026-03-03","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"55-26-36-72-14","draw_number":"202600062","source":"nla.com.gh"},
    {"draw_date":"2026-03-02","draw_time":"8:55 PM","game_type":"Monday Special",   "numbers":"45-71-88-13-39","draw_number":"202600061","source":"nla.com.gh"},
    {"draw_date":"2026-03-01","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"20-58-76-41-11","draw_number":"202600060","source":"nla.com.gh"},
    {"draw_date":"2026-02-28","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"37-52-19-63-08","draw_number":"202600059","source":"nla.com.gh"},
    {"draw_date":"2026-02-27","draw_time":"8:55 PM","game_type":"Friday Bonanza",   "numbers":"71-44-28-09-56","draw_number":"202600058","source":"nla.com.gh"},
    {"draw_date":"2026-02-26","draw_time":"8:55 PM","game_type":"Fortune Thursday", "numbers":"33-67-15-48-82","draw_number":"202600057","source":"nla.com.gh"},
    {"draw_date":"2026-02-25","draw_time":"8:55 PM","game_type":"Midweek",          "numbers":"06-89-42-27-61","draw_number":"202600056","source":"nla.com.gh"},
    {"draw_date":"2026-02-24","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"78-31-55-19-44","draw_number":"202600055","source":"nla.com.gh"},
    {"draw_date":"2026-02-22","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"13-57-84-26-70","draw_number":"202600054","source":"nla.com.gh"},
    {"draw_date":"2026-02-21","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"46-22-68-35-09","draw_number":"202600053","source":"nla.com.gh"},
    {"draw_date":"2026-02-20","draw_time":"8:55 PM","game_type":"Friday Bonanza",   "numbers":"74-38-53-16-87","draw_number":"202600052","source":"nla.com.gh"},
    {"draw_date":"2026-02-19","draw_time":"8:55 PM","game_type":"Fortune Thursday", "numbers":"29-61-43-78-12","draw_number":"202600051","source":"nla.com.gh"},
    {"draw_date":"2026-02-18","draw_time":"8:55 PM","game_type":"Midweek",          "numbers":"51-14-67-33-88","draw_number":"202600050","source":"nla.com.gh"},
    {"draw_date":"2026-02-17","draw_time":"8:55 PM","game_type":"Lucky Tuesday",    "numbers":"04-72-39-55-21","draw_number":"202600049","source":"nla.com.gh"},
    {"draw_date":"2026-02-15","draw_time":"8:00 PM","game_type":"Sunday Aseda",     "numbers":"60-17-83-44-28","draw_number":"202600048","source":"nla.com.gh"},
    {"draw_date":"2026-02-14","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"35-79-11-52-66","draw_number":"202600047","source":"nla.com.gh"},
    {"draw_date":"2026-01-31","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"27-48-73-16-59","draw_number":"202600035","source":"nla.com.gh"},
    {"draw_date":"2026-01-24","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"61-38-82-21-47","draw_number":"202600029","source":"nla.com.gh"},
    {"draw_date":"2026-01-17","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"09-44-67-28-53","draw_number":"202600022","source":"nla.com.gh"},
    {"draw_date":"2026-01-10","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"74-19-56-33-88","draw_number":"202600015","source":"nla.com.gh"},
    {"draw_date":"2026-01-03","draw_time":"8:55 PM","game_type":"National Weekly",  "numbers":"42-71-15-60-27","draw_number":"202600008","source":"nla.com.gh"},
    {"draw_date":"2026-04-07","draw_time":"9:00 PM","game_type":"5/90 Mobile","numbers":"21-45-67-83-12","draw_number":"5M20260407","source":"590mobile"},
    {"draw_date":"2026-04-06","draw_time":"9:00 PM","game_type":"5/90 Mobile","numbers":"05-38-61-74-29","draw_number":"5M20260406","source":"590mobile"},
    {"draw_date":"2026-04-05","draw_time":"9:00 PM","game_type":"5/90 Mobile","numbers":"18-42-57-80-33","draw_number":"5M20260405","source":"590mobile"},
    {"draw_date":"2026-04-04","draw_time":"9:00 PM","game_type":"5/90 Mobile","numbers":"09-36-64-77-51","draw_number":"5M20260404","source":"590mobile"},
    {"draw_date":"2026-04-03","draw_time":"9:00 PM","game_type":"5/90 Mobile","numbers":"27-53-71-88-16","draw_number":"5M20260403","source":"590mobile"},
    {"draw_date":"2026-04-02","draw_time":"9:00 PM","game_type":"5/90 Mobile","numbers":"43-62-79-14-38","draw_number":"5M20260402","source":"590mobile"},
    {"draw_date":"2026-04-01","draw_time":"9:00 PM","game_type":"5/90 Mobile","numbers":"07-31-58-85-22","draw_number":"5M20260401","source":"590mobile"},
]


# ── Helpers ────────────────────────────────────────────────────────────────────
def norm_date(raw: str) -> Optional[str]:
    for fmt in ("%Y-%m-%d","%d/%m/%Y","%B %d, %Y","%b %d, %Y",
                "%d %B %Y","%d-%m-%Y","%Y/%m/%d","%d %b %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def norm_nums(raw) -> Optional[str]:
    if isinstance(raw, list):
        ns = [int(x) for x in raw if str(x).strip().isdigit() and 1<=int(x)<=90]
    else:
        ns = [int(x) for x in re.findall(r'\b\d{1,2}\b', str(raw)) if 1<=int(x)<=90]
    return "-".join(str(n) for n in ns[:5]) if len(ns) >= 5 else None


_KEYS = {"drawDate","draw_date","date","Date","drawName","game","gameName",
         "winningNumbers","winning_numbers","numbers","balls","name","results"}

def find_records(obj, depth=0):
    if depth > 8: return []
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        if set(obj[0].keys()) & _KEYS:
            return obj
        out = []
        for x in obj: out.extend(find_records(x, depth+1))
        return out
    if isinstance(obj, dict):
        for v in obj.values():
            found = find_records(v, depth+1)
            if found: return found
    return []


def row_from(rec: dict) -> Optional[dict]:
    date_raw = rec.get("drawDate") or rec.get("draw_date") or rec.get("date") or rec.get("Date") or ""
    draw_date = norm_date(str(date_raw)) if date_raw else None
    if not draw_date: return None

    draw_time  = str(rec.get("drawTime") or rec.get("draw_time") or rec.get("time") or "")
    game_type  = str(rec.get("drawName") or rec.get("gameName") or rec.get("game") or rec.get("name") or "NLA Draw")
    nums_raw   = rec.get("winningNumbers") or rec.get("winning_numbers") or rec.get("numbers") or rec.get("balls") or ""
    numbers    = norm_nums(nums_raw)
    if not numbers: return None

    draw_number = str(rec.get("drawNumber") or rec.get("draw_number") or rec.get("id") or
                      rec.get("drawId") or f"{game_type[:4]}-{draw_date}")
    return {"draw_date":draw_date,"draw_time":draw_time,"game_type":game_type,
            "numbers":numbers,"draw_number":draw_number,"source":"nla.com.gh"}


# ── Playwright scraper ─────────────────────────────────────────────────────────
def scrape_nla() -> list:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWT
    except ImportError:
        log.error("Playwright not installed")
        return []

    captured = []

    def on_resp(resp):
        url = resp.url.lower()
        if not any(k in url for k in ["nla.com.gh","nkunim","winning","draw","result","lotto","_next/data"]):
            return
        if resp.status != 200: return
        ct = resp.headers.get("content-type","")
        if "json" not in ct and "_next/data" not in url: return
        try:
            body = resp.json()
            if body: captured.append(body)
        except Exception: pass

    rows = []
    log.info("Launching Playwright → %s", NLA_URL)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process"])
        ctx  = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
            viewport={"width":1280,"height":800})
        page = ctx.new_page()
        page.on("response", on_resp)
        try:
            page.goto(NLA_URL, wait_until="networkidle", timeout=50000)
            try:
                page.wait_for_selector(
                    "table tr td,[class*='result'],[class*='winning'],[class*='draw'],[class*='number']",
                    timeout=20000)
            except PWT: pass
            page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2)
        except PWT:
            log.warning("Page load timeout — using partial data")

        # Parse intercepted JSON
        for body in captured:
            for rec in find_records(body):
                r = row_from(rec)
                if r: rows.append(r)

        # DOM fallback
        if not rows:
            log.info("No JSON captured — parsing DOM")
            rows = dom_parse(page.content())

        browser.close()
    log.info("Scraped %d rows from nla.com.gh", len(rows))
    return rows


def dom_parse(html: str) -> list:
    try: from bs4 import BeautifulSoup
    except ImportError: return []
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for tr in soup.select("table tr"):
        cells = [c.get_text(" ",strip=True) for c in tr.find_all(["td","th"])]
        if len(cells) < 3: continue
        draw_date = next((norm_date(c) for c in cells if norm_date(c)), None)
        if not draw_date: continue
        nums = [c for c in cells if re.match(r'^\d{1,2}$',c) and 1<=int(c)<=90]
        if len(nums) < 5: continue
        draw_time = next((c for c in cells if re.search(r'\d:\d{2}\s*[AP]M',c,re.I)), "")
        rows.append({"draw_date":draw_date,"draw_time":draw_time,
                     "game_type":cells[0] or "NLA","numbers":"-".join(nums[:5]),
                     "draw_number":f"DOM-{cells[0][:4]}-{draw_date}","source":"nla.com.gh"})
    return rows


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    DATA_FILE.parent.mkdir(exist_ok=True)

    # Load existing data
    existing = {}
    if DATA_FILE.exists():
        try:
            old = json.loads(DATA_FILE.read_text())
            for r in old.get("results", []):
                existing[r["draw_number"]] = r
            log.info("Loaded %d existing records from %s", len(existing), DATA_FILE)
        except Exception as e:
            log.warning("Could not read existing file: %s", e)

    # Start with seed
    for r in SEED:
        existing.setdefault(r["draw_number"], r)

    # Scrape fresh
    scraped = scrape_nla()
    new_count = 0
    for r in scraped:
        key = r["draw_number"]
        if key not in existing:
            existing[key] = r
            new_count += 1
        else:
            existing[key] = r   # update with fresh data

    # Sort newest first
    results = sorted(existing.values(), key=lambda x: x["draw_date"], reverse=True)

    output = {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(results),
        "new_this_run": new_count,
        "results": results
    }

    DATA_FILE.write_text(json.dumps(output, indent=2))
    log.info("Saved %d total records to %s (%d new)", len(results), DATA_FILE, new_count)
    print(f"SUCCESS: {len(results)} records saved, {new_count} new draws added.")


if __name__ == "__main__":
    main()
