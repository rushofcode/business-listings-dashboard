# Business Listings Dashboard

Full-stack internship assignment project built with **React + Vite**, **FastAPI**, and **MySQL**. The dashboard displays city-wise, category-wise, and source-wise counts, KPI cards, and a searchable, paginated listings table.

> **Data transparency:** the included 650-row dataset is synthetic test data generated for demonstrating the application. It is not a list of verified real businesses and was not scraped from Google Maps or Justdial. If the evaluator requires actual data, use a source whose terms permit collection and explain the collection process accurately.

## Features

- Responsive React dashboard with KPI cards and Recharts visualizations.
- FastAPI REST API with Swagger documentation.
- MySQL `listing_master` table and indexes.
- Bulk JSON insertion endpoint.
- CSV upload endpoint with row validation and size limits.
- City-, category-, and source-wise aggregate endpoints.
- Searchable and paginated listings table.
- Deterministic synthetic dataset of 650 records, CSV, SQL schema and SQL dump.
- Database credentials read from environment variables.
- Optional OpenStreetMap import example.

## Project structure

```text
business_listings_dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── .env.example
│   └── requirements.txt
├── data/
│   ├── schema.sql
│   ├── business_listings_db_dump.sql
│   ├── sample_listings.csv
│   └── generate_sample_data.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── DEMO_SCRIPT.md
├── README.md
└── .gitignore
```

## Prerequisites

- Python 3.10 or newer (Python 3.11 recommended)
- Node.js 20.19+ recommended for the Vite version in `package.json`
- npm
- MySQL 8.x and MySQL Workbench
- Git (for submission)

## Run locally on Windows

### 1. Create the database and sample records

**Recommended easiest method:** Open `data/business_listings_db_dump.sql` in MySQL Workbench and execute the script. It creates `business_listings_db`, creates `listing_master`, and inserts 650 synthetic records.

Alternatively, run `data/schema.sql` first and import the CSV through the API in step 4. **Do not run both the full dump and the CSV import unless you intend to create duplicate records.**

### 2. Configure the backend

Open PowerShell in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set `DB_PASSWORD` to your MySQL password. If your MySQL user/database differs, update `DB_HOST`, `DB_PORT`, `DB_USER`, and `DB_NAME` too. Keep `.env` private; it is ignored by Git.

### 3. Start FastAPI

Still in the `backend` folder, with the virtual environment active:

```powershell
uvicorn app.main:app --reload
```

Check:
- API health: http://127.0.0.1:8000/api/health
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

If PowerShell says script execution is disabled when activating the environment, use Command Prompt instead and run `.venv\Scripts\activate.bat`, or follow your organization's Python environment policy.

### 4. Start React

Open a **second** terminal in the project root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the local URL Vite prints, usually http://localhost:5173.

The frontend `.env.example` sets `VITE_API_BASE_URL=http://127.0.0.1:8000`. Restart Vite after changing environment variables.

### 5. Import CSV instead of the SQL dump (optional)

If you ran only `data/schema.sql`, start the backend and then, from the project root, run:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/listings/upload-csv" `
  -F "file=@data/sample_listings.csv"
```

The endpoint reports total rows, inserted rows, skipped rows and a small list of validation errors. It accepts up to 5 MB and 5,000 rows per upload.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check database connectivity |
| POST | `/api/listings/bulk` | Insert validated JSON listings |
| POST | `/api/listings/upload-csv` | Import listings from CSV |
| GET | `/api/listings` | Search and paginate listings |
| GET | `/api/dashboard/summary` | KPI counts |
| GET | `/api/dashboard/city-wise` | Listing count per city |
| GET | `/api/dashboard/category-wise` | Listing count per category |
| GET | `/api/dashboard/source-wise` | Listing count per source |

### Example bulk insert request

Use Swagger UI's `POST /api/listings/bulk` endpoint with this JSON:

```json
{
  "listings": [
    {
      "business_name": "Demo Cafe",
      "category": "Cafe",
      "city": "Thane",
      "address": "Demo Road, Thane, Maharashtra",
      "phone": null,
      "source": "Manual Demo"
    }
  ]
}
```

The `phone` field is optional because the assignment specifies phone numbers only when available.

### Example response formats

Summary:

```json
{
  "total_listings": 650,
  "total_cities": 14,
  "total_categories": 12,
  "total_sources": 4
}
```

City/category/source aggregates are arrays of objects, e.g.:

```json
[
  {"city": "Mumbai", "count": 100},
  {"city": "Delhi", "count": 90}
]
```

Exact counts depend on the dataset currently in MySQL.

## Dataset generation

The existing sample files contain 650 deterministic synthetic records. To regenerate them:

```powershell
cd data
python generate_sample_data.py
```

This overwrites `sample_listings.csv` and `business_listings_db_dump.sql`. Regeneration does not automatically update the database; import the new dump/CSV if required.

## Real-data collection note

The assignment permits sample data when scraping is blocked, provided the approach is explained. Direct scraping of Google Maps, Justdial, or Sulekha may be restricted by their terms and technical controls. Do not bypass logins, CAPTCHAs, rate limits, or access restrictions.

If you choose to use real data, select a source and method permitted for your use, preserve source attribution, and explain its limitations. The current project does **not** claim that its synthetic sample records are real or scraped.

## Challenges and solutions (for README/demo)

1. **Scraping access and terms:** rather than misrepresenting fake records, the project includes transparent synthetic data for validating the complete stack.
2. **Bulk imports:** Pydantic validation and CSV row checks identify invalid records; parameterized SQL protects values from being treated as SQL.
3. **Performance:** city/category/source counts are calculated by MySQL `GROUP BY`, not by downloading every record into React.
4. **Frontend/backend integration:** a dedicated `api.js` module keeps API calls in one place and documents the response field names.
5. **Database configuration:** credentials are stored in `backend/.env`, excluded from version control.

## Common errors

- **503 / cannot connect to database:** confirm MySQL is running, the database dump has been imported, and `backend/.env` has correct credentials.
- **Frontend cannot reach API:** start FastAPI and check `VITE_API_BASE_URL` in `frontend/.env`.
- **CORS error:** confirm the frontend origin is listed in `CORS_ORIGINS` in `backend/.env`, then restart FastAPI.
- **No chart data:** check that records exist with `SELECT COUNT(*) FROM listing_master;`.
- **Duplicate rows:** importing the SQL dump and CSV both inserts the dataset. Use only one import method for a clean initial setup.
- **Node version error:** install a supported current Node.js LTS version and reopen the terminal.

## GitHub submission checklist

1. Run the SQL dump in MySQL Workbench.
2. Start backend and frontend; confirm charts show data and table search/pagination work.
3. Test `/api/health` and the dashboard endpoints in Swagger.
4. Confirm `.env`, `.venv`, `node_modules`, and build outputs are not committed.
5. Push the project root to GitHub so `backend/`, `frontend/`, and `data/` remain separate.
6. Add your own name and any actual changes to the README if required by your institute.
7. Record the 3–5 minute demo described in `DEMO_SCRIPT.md`.
8. Clearly disclose that included records are synthetic unless you replace them with genuinely collected data.

## Limitations

- Included records are synthetic, not verified businesses.
- The optional real-data approach depends on source coverage and permission; 500 records cannot be guaranteed for every city/source.
- Authentication, production hosting, and automated deployment are outside this assignment's current scope.
