"""Business Listings Dashboard - FastAPI backend.

Run from the backend folder:  uvicorn app.main:app --reload
Docs:                         http://127.0.0.1:8000/docs
"""
import csv
import io
import os
from typing import Optional

import pymysql
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .database import get_db
from .schemas import BulkListingsRequest, ListingIn

app = FastAPI(title="Business Listings API", version="1.0.0")

origins = [o.strip() for o in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUIRED_COLUMNS = ["business_name", "category", "city", "address", "phone"]
MAX_CSV_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_CSV_ROWS = 5000


@app.exception_handler(pymysql.MySQLError)
async def mysql_error_handler(request: Request, exc: pymysql.MySQLError):
    # Generic message to the client; do not leak SQL details.
    return JSONResponse(status_code=500, content={"detail": "Database error. Please try again."})


def insert_listings(conn, rows: list) -> int:
    """Insert validated ListingIn objects using a parameterized query."""
    sql = ("INSERT INTO listing_master (business_name, category, city, address, phone, source) "
           "VALUES (%s, %s, %s, %s, %s, %s)")
    data = [(r.business_name, r.category, r.city, r.address, r.phone, r.source) for r in rows]
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, data)
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        raise
    return len(data)


def escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@app.get("/api/health")
def health(conn=Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 AS ok")
        cur.fetchone()
    return {"status": "ok"}


# ---------------------------------------------------------------- INSERT
@app.post("/api/listings/bulk", status_code=201)
def bulk_insert(payload: BulkListingsRequest, conn=Depends(get_db)):
    inserted = insert_listings(conn, payload.listings)
    return {"inserted": inserted, "message": f"{inserted} listings inserted successfully."}


@app.post("/api/listings/upload-csv", status_code=201)
def upload_csv(file: UploadFile = File(...), conn=Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")
    raw = file.file.read(MAX_CSV_BYTES + 1)
    if len(raw) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="CSV is larger than 5 MB.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.")

    reader = csv.DictReader(io.StringIO(text))
    headers = [(h or "").strip().lower() for h in (reader.fieldnames or [])]
    missing = [c for c in REQUIRED_COLUMNS if c not in headers]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing CSV columns: {', '.join(missing)}")
    reader.fieldnames = headers

    valid, errors, total = [], [], 0
    for line_no, row in enumerate(reader, start=2):  # line 1 is the header
        total += 1
        if total > MAX_CSV_ROWS:
            raise HTTPException(status_code=413, detail=f"CSV has more than {MAX_CSV_ROWS} rows.")
        try:
            valid.append(ListingIn(
                business_name=row.get("business_name") or "",
                category=row.get("category") or "",
                city=row.get("city") or "",
                address=row.get("address") or "",
                phone=row.get("phone") or None,
                source=(row.get("source") or "").strip() or "CSV Import",
            ))
        except ValidationError as e:
            first = e.errors()[0]
            errors.append({"row": line_no, "error": f"{first['loc'][0]}: {first['msg']}"})

    inserted = insert_listings(conn, valid) if valid else 0
    return {
        "total_rows": total,
        "inserted": inserted,
        "skipped": len(errors),
        "errors": errors[:20],
    }


# ---------------------------------------------------------------- READ
@app.get("/api/listings")
def get_listings(
    search: Optional[str] = Query(None, max_length=100),
    city: Optional[str] = Query(None, max_length=100),
    category: Optional[str] = Query(None, max_length=100),
    source: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn=Depends(get_db),
):
    where, params = [], []
    if search and search.strip():
        like = f"%{escape_like(search.strip())}%"
        where.append("(business_name LIKE %s OR category LIKE %s OR city LIKE %s "
                     "OR address LIKE %s OR phone LIKE %s OR source LIKE %s)")
        params.extend([like] * 6)
    for column, value in (("city", city), ("category", category), ("source", source)):
        if value and value.strip():
            where.append(f"{column} = %s")  # column names are fixed above, values are parameters
            params.append(value.strip())
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total FROM listing_master {where_sql}", params)
        total = cur.fetchone()["total"]
        cur.execute(
            "SELECT id, business_name, category, city, address, phone, source, created_at "
            f"FROM listing_master {where_sql} ORDER BY id DESC LIMIT %s OFFSET %s",
            params + [page_size, (page - 1) * page_size],
        )
        items = cur.fetchall()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# ---------------------------------------------------------------- DASHBOARD
@app.get("/api/dashboard/summary")
def dashboard_summary(conn=Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS total_listings, COUNT(DISTINCT city) AS total_cities, "
            "COUNT(DISTINCT category) AS total_categories, COUNT(DISTINCT source) AS total_sources "
            "FROM listing_master"
        )
        return cur.fetchone()


def group_count(conn, column: str):
    assert column in ("city", "category", "source")  # whitelist: never from user input
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT {column} AS {column}, COUNT(*) AS count FROM listing_master "
            f"GROUP BY {column} ORDER BY count DESC, {column} ASC"
        )
        return cur.fetchall()


@app.get("/api/dashboard/city-wise")
def city_wise(conn=Depends(get_db)):
    return group_count(conn, "city")


@app.get("/api/dashboard/category-wise")
def category_wise(conn=Depends(get_db)):
    return group_count(conn, "category")


@app.get("/api/dashboard/source-wise")
def source_wise(conn=Depends(get_db)):
    return group_count(conn, "source")
