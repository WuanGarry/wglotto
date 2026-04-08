"""
WUAN GARRY - Ghana NLA Lotto Analysis System
Flask Backend - Serves API + Frontend
"""
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3, os, logging
from datetime import datetime
from scraper import scrape_results, init_db, seed_db
from predictor import generate_all_predictions, analyse_numbers

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)

DB_PATH = os.environ.get("DB_PATH", "lotto.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Serve frontend ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ── API: latest results ───────────────────────────────────────────────────────
@app.route("/api/results")
def api_results():
    limit  = request.args.get("limit",  50,  type=int)
    offset = request.args.get("offset", 0,   type=int)
    game   = request.args.get("game",   "",  type=str)
    date_from = request.args.get("from", "", type=str)
    date_to   = request.args.get("to",   "", type=str)

    conn = get_db()
    query = "SELECT * FROM results WHERE 1=1"
    params = []
    if game:
        query += " AND game_type LIKE ?"
        params.append(f"%{game}%")
    if date_from:
        query += " AND draw_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND draw_date <= ?"
        params.append(date_to)
    query += " ORDER BY draw_date DESC, draw_time DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(query, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]
    conn.close()
    return jsonify({
        "total": total,
        "results": [dict(r) for r in rows]
    })

# ── API: analysis ─────────────────────────────────────────────────────────────
@app.route("/api/analysis")
def api_analysis():
    game = request.args.get("game", "", type=str)
    conn = get_db()
    query = "SELECT numbers FROM results WHERE 1=1"
    params = []
    if game:
        query += " AND game_type LIKE ?"
        params.append(f"%{game}%")
    rows = conn.execute(query, params).fetchall()
    conn.close()
    all_nums = []
    for row in rows:
        nums = [int(x) for x in str(row["numbers"]).split("-") if x.strip().isdigit()]
        all_nums.extend(nums)
    return jsonify(analyse_numbers(all_nums))

# ── API: predictions ──────────────────────────────────────────────────────────
@app.route("/api/predictions")
def api_predictions():
    game = request.args.get("game", "", type=str)
    conn = get_db()
    query = "SELECT numbers FROM results WHERE 1=1"
    params = []
    if game:
        query += " AND game_type LIKE ?"
        params.append(f"%{game}%")
    rows = conn.execute(query, params).fetchall()
    conn.close()
    all_nums = []
    for row in rows:
        nums = [int(x) for x in str(row["numbers"]).split("-") if x.strip().isdigit()]
        all_nums.extend(nums)
    return jsonify(generate_all_predictions(all_nums))

# ── API: refresh (manual scrape trigger) ──────────────────────────────────────
@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    try:
        new_count = scrape_results(DB_PATH)
        return jsonify({"success": True, "new_records": new_count, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        logging.error(f"Scrape error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ── API: game types list ───────────────────────────────────────────────────────
@app.route("/api/games")
def api_games():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT game_type FROM results ORDER BY game_type").fetchall()
    conn.close()
    return jsonify([r["game_type"] for r in rows])

# ── API: stats summary ─────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM results").fetchone()["c"]
    latest = conn.execute("SELECT draw_date, draw_time, game_type, numbers FROM results ORDER BY draw_date DESC LIMIT 1").fetchone()
    games = conn.execute("SELECT COUNT(DISTINCT game_type) as c FROM results").fetchone()["c"]
    conn.close()
    return jsonify({
        "total_draws": total,
        "game_types": games,
        "latest": dict(latest) if latest else None,
        "last_updated": datetime.now().isoformat()
    })

if __name__ == "__main__":
    init_db(DB_PATH)
    seed_db(DB_PATH)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
