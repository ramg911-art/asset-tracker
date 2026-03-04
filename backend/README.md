# Enterprise Asset Management – Backend

Production-grade FastAPI backend with PostgreSQL, SQLAlchemy 2.0, Alembic, Pydantic v2, and JWT authentication.

## Stack

- **Python 3.11**
- **FastAPI**
- **PostgreSQL** (async via asyncpg)
- **SQLAlchemy 2.0** (async)
- **Alembic** migrations
- **Pydantic v2**
- **JWT** (python-jose) + **passlib** (bcrypt)

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. Create a PostgreSQL database and set the URL (optional; default below):

   ```bash
   set DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/asset_tracker
   ```

   For Alembic (sync) use a sync URL in `.env` if needed, e.g. `postgresql://user:pass@localhost:5432/asset_tracker`.

3. Run migrations:

   ```bash
   alembic upgrade head
   ```

4. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

   API: http://127.0.0.1:8000  
   Docs: http://127.0.0.1:8000/docs  

## Project layout

```
backend/
  app/
    main.py           # FastAPI app, CORS, router registration
    config.py         # Pydantic settings (env)
    database.py       # Async engine, session, Base
    models/           # SQLAlchemy models (all tables)
    schemas/          # Pydantic request/response
    routers/          # API routes (auth, assets, locations, …)
    services/         # Business logic (e.g. auth)
    auth/             # JWT + password hashing
    utils/            # Dependencies, audit, geo
  alembic/
    versions/         # Migrations (001_initial_schema.py)
  requirements.txt
```

## Auth

- **POST /auth/register** – Register (email, password, full_name)
- **POST /auth/login** – Login (email, password) → JWT
- **GET /auth/me** – Current user (Bearer token)

All other routes require `Authorization: Bearer <token>`.

## Core routers (CRUD)

- **/assets** – Assets (search, filter by status, category, location)
- **/locations** – Hierarchical locations (parent_id, lat/lon, radius)
- **/categories** – Asset categories
- **/departments** – Departments
- **/vendors** – Vendors
- **/repairs** – Asset repairs
- **/movements** – Asset movements (POST updates `asset.current_location_id`)
- **/maintenance** – Maintenance plans
- **/verification** – Campaigns, **POST /verification/scan** (QR scan + location detection), **POST /verification/scans/{id}/photo**
- **/documents** – Asset documents (file upload)
- **/labels** – **POST /labels/generate** (asset_ids → PDF QR labels), **GET /labels/{id}/download**
- **/reports** – **GET /reports/summary**, **GET /reports/audit**

## Behaviour

- **Asset movement**: `POST /movements` creates a movement and sets `asset.current_location_id` to `to_location_id`.
- **Verification scan**: `POST /verification/scan` with `asset_tag`, `campaign_id`, optional `lat`/`lon` or `manual_location_id`. If lat/lon present, location is detected by radius; otherwise manual location is used. `location_source`: gps | manual | device_last_location.
- **Labels**: `POST /labels/generate` with `asset_ids` returns a batch record; PDF is downloaded via `GET /labels/{batch_id}/download`.
- **Uploads**: Documents under **/documents** (asset_id + file), verification photos under **/verification/scans/{id}/photo**. Stored under `uploads/` (documents, verification).
- **Audit**: Update/delete on assets and locations write to `audit_logs`. Same pattern can be applied to other routers via `log_audit()`.

## Indexes

Indexes are on: `asset_tag`, `serial_number`, `current_location_id`, `asset_movements.asset_id`, `asset_verifications.asset_id`, `asset_events.asset_id` (and in migration).

## Config (env)

- `DATABASE_URL` – PostgreSQL URL (async: `postgresql+asyncpg://...`)
- `SECRET_KEY` – JWT secret
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `UPLOAD_DIR` – default `uploads`
- `ALLOWED_DOCUMENT_EXTENSIONS`, `ALLOWED_IMAGE_EXTENSIONS`
