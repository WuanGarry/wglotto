# WUAN GARRY — Ghana NLA Lotto Analysis System

A full-stack Ghana National Lottery Authority (NLA) lotto analysis system with live scraping, statistical predictions, charts, and permutation generation.

---

## Features

- **Live NLA Results** scraped from easywin.ng (covers all NLA games + 5/90 Mobile)
- **Historical Table** with date-range filtering and sorting
- **Hot/Cold Analysis** — frequency, odd/even, high/low, pairs, triplets
- **5 Prediction Models** — frequency, weighted random, hot-cold blend, odd-even balanced, high-low split
- **Charts** — frequency bar, monthly trend, odd/even doughnut, range distribution
- **Permutation Generator** — C(n, r) combinations for your chosen numbers
- **Auto-refresh** every 6 hours via background scheduler
- **Covers**: National Weekly · Monday Special · Lucky Tuesday · Midweek · Fortune Thursday · Friday Bonanza · Sunday Aseda · **5/90 Mobile (590mobile.com.gh)**

---

## File Structure

```
wuan-garry/
├── app.py            # Flask backend + API routes
├── scraper.py        # NLA result scraper + seed data (Mar–Apr 2026)
├── predictor.py      # All 5 prediction models
├── scheduler.py      # Background 6-hour auto-scrape thread
├── wsgi.py           # Gunicorn entry point
├── requirements.txt  # Python dependencies
├── render.yaml       # Render.com deployment config
├── .gitignore
└── templates/
    └── index.html    # Full frontend (single file)
```

---

## Local Development

```bash
# 1. Clone and enter
git clone https://github.com/YOUR_USERNAME/wuan-garry.git
cd wuan-garry

# 2. Create virtualenv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install deps
pip install -r requirements.txt

# 4. Run locally
python app.py
# Opens on http://localhost:5000
```

---

## Deploy to Render (Step-by-Step)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit – WUAN GARRY lotto system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/wuan-garry.git
git push -u origin main
```

### Step 2 — Create Render Web Service

1. Go to **https://render.com** → Sign up / Log in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account and select the **wuan-garry** repo
4. Fill in:

| Field | Value |
|---|---|
| Name | `wuan-garry-lotto` |
| Region | Frankfurt EU (closest to Ghana) |
| Branch | `main` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn wsgi:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT --timeout 120` |

5. Click **"Advanced"** → Add Environment Variable:
   - Key: `DB_PATH`  Value: `/opt/render/project/src/lotto.db`

6. Click **"Add Disk"** (for persistent SQLite):
   - Name: `lotto-data`
   - Mount Path: `/opt/render/project/src`
   - Size: 1 GB

7. Click **"Create Web Service"**

### Step 3 — Done!

Render will build and deploy. Your URL will be:
```
https://wuan-garry-lotto.onrender.com
```

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Frontend UI |
| `GET /api/results` | Paginated results (params: `limit`, `offset`, `game`, `from`, `to`) |
| `GET /api/analysis` | Hot/cold/odd-even stats (param: `game`) |
| `GET /api/predictions` | 5 predictions (param: `game`) |
| `GET /api/games` | List of game types |
| `GET /api/stats` | Summary stats |
| `POST /api/refresh` | Trigger manual scrape |

---

## Data Sources

| Source | URL |
|---|---|
| Primary scraper | https://easywin.ng/DrawResult/GhanaGame |
| Official NLA | https://www.nla.com.gh/winning-numbers |
| 5/90 Mobile | https://www.590mobile.com.gh/results |

---

## ⚠ Disclaimer

> These predictions are based on statistical frequency analysis and **do not guarantee winning**. Lottery is a game of chance. Play responsibly. 18+

---

## License

MIT — Free to use and modify for personal or educational purposes.
"# wglotto" 
