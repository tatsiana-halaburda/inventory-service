# Inventory service

FastAPI app for `[Tanya_Inventory]` (warehouses, ingredients, stock). Port **8001**.

Split from the [monorepo](../Azure/README.md). Related repos: [ordering-service](https://github.com/tatsiana-halaburda/ordering-service), [feedback-service](https://github.com/tatsiana-halaburda/feedback-service).

## Environment

Copy `.env.example` → `.env`.

| Variable | Required |
|----------|----------|
| `DB_SERVER`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` | Yes (unless `AZURE_SQL_CONNECTION_STRING`) |
| `AZURE_SQL_CONNECTION_STRING` | No — overrides `DB_*` |
| `AZURE_SERVICEBUS_LISTEN_CONNECTION_STRING`, `AZURE_SERVICEBUS_QUEUE_NAME` | No — enables Practice 3 queue listener |

## Azure SQL

Run scripts in order against your database (same order as monorepo):

1. `sql/01_schemas.sql` … `sql/05_seed.sql`

## Run

```bash
docker compose up --build -d
```

Local: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

```bash
uvicorn services.inventory.main:app --host 127.0.0.1 --port 8001
```

OpenAPI: `http://127.0.0.1:8001/docs`
