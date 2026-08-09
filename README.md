# Car parser

<img width="1920" height="929" alt="image" src="https://github.com/user-attachments/assets/6e6d7e6f-22c4-4ddd-9f3c-f30015353e75" />


Pulls used car listings from [Encar](https://www.encar.com/), the biggest used car marketplace in Korea, saves them to Postgres, and shows them in a React app. Prices get converted from won to dollars, and manufacturer names get translated from Korean, so the listings are actually readable.

There's a scheduled job that re-scrapes once a day and updates prices on listings that are already in the database.

**Live:** https://xeiton8.github.io/car-parser/ 

Currently frontend only, running on a saved snapshot.

---

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy 2.0 (async), asyncpg, Alembic, APScheduler, httpx
- **Frontend**: React, TypeScript, Vite, CSS
- **Database**: PostgreSQL
- **Other**: Docker

---

## How it works

```
Encar search API
      │
      ▼
  parser  ──── 5 requests at a time, retries with backoff
      │        Korean brand names -> English
      │        KRW → USD
      │        drop broken rows, dedupe by listing id
      ▼
 repository ── upsert into Postgres (ON CONFLICT DO UPDATE)
      │
      ▼
  FastAPI  ──── GET /cars
      │
      ▼
   React
```

A daily cron job at 03:00 runs the same flow, so listings that are already stored get their price and mileage refreshed instead of duplicated.

### Problems I had to solve

<img width="1920" height="929" alt="image" src="https://github.com/user-attachments/assets/b081bd16-5379-434d-890c-638f1f417a0b" />

1. **A bug I wrote, then found.** The parser reads 5 pages at once, no more. A failed page
is retried up to 5 times, waiting 2s-4s-8s. If it still fails, that page is
skipped and the rest of the run goes on. At first each retry was a recursive call. But slots
are not re-entrant, so every retry grabbed one and then asked for the next. A page that
failed 5 times held all five and the whole run hung. Now it's a loop, and
the waiting happens outside the slot.

2. **Listings that come back.** The same car shows up in the feed day after day, sometimes with a lower price. So `source_id` (Encar's own listing id) has a unique index, and inserts go through Postgres `ON CONFLICT DO UPDATE`: one statement for the whole batch, updating price, mileage and image instead of creating a second row. Duplicates inside a single batch get filtered out before that, keyed by the same id.

3. **Pages that don't shift.** Every row in a batch is written with the same `created_at`, so ordering by that column alone left the order of equal rows up to Postgres. Which meant a car could show up on two pages, or on none. The sort key is `created_at DESC, id DESC` now. `id` is unique, so the order is total and pagination is stable.

4. **Messy data.** The API returns years like `202003`, prices in units of 10,000 won, manufacturer names in Korean, and photos as an unordered array. Each row is parsed inside a try/except. If one listing is malformed it gets logged and dropped, and the rest of the batch still goes through.

---

## API

| Method | Path | What it does |
|---|---|---|
| `GET` | `/cars?skip=0&limit=20` | Returns stored listings, newest first |
| `POST` | `/cars/refresh` | Triggers a scrape right now instead of waiting for the cron |

Docs are at `/docs` once it's running.

---

## Running it

**Backend**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# .env in the backend folder
echo 'database_url=postgresql+asyncpg://user:password@localhost:5432/cars' > .env

alembic upgrade head
uvicorn app.main:app --reload
```

Then hit `POST /cars/refresh` once to fill the database, otherwise there's nothing to show.

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Docker (backend only)**

```bash
cd backend
docker build -t car-parser .
docker run -p 8000:8000 --env-file .env car-parser
```

The image runs migrations first, then starts the server.

---

## Project structure

```
backend/
  app/
    api/          routes
    services/     use cases
    repositories/ database logic
    parsers/      the Encar scraper
    models/       SQLAlchemy tables
    schemas/      Pydantic models
    tasks/        the daily scheduler
    utils/        http client, currency
    db/           engine and session
    core/         settings
  alembic/        migrations

frontend/
  src/
    components/   CarCard, CarGrid, CarSkeleton, Header, Hero
```

The backend is split into layers on purpose. Routes don't touch the database, and the parser doesn't know Postgres exists.

---

## Known limitations

- **The frontend is not wired to the API yet.** It renders a saved snapshot of scraped data and fakes the network delay so the loading states are visible.
- **The KRW to USD rate is hardcoded.** It should come from an exchange rate API.
- **Only manufacturer names are translated.** Model names are still in Korean, since there's no clean mapping for them.
- **Offset pagination.** The sort key is deterministic, so pages are stable, but cursor-based would be better once the table grows.
- **No tests.** The retry loop is where I'd start.

## What I'd add next

- Connect the frontend to the API
- Filters: brand, year range, price range, mileage
- Price history per listing, so you can see when something gets cheaper
