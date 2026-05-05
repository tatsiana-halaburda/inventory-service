# Inventory service

FastAPI app for `[Tanya_Inventory]` (warehouses, ingredients, stock). Port **8001**.

Split from the [monorepo](../Azure/README.md). Related repos: [ordering-service](https://github.com/tatsiana-halaburda/ordering-service), [feedback-service](https://github.com/tatsiana-halaburda/feedback-service).

## Business logic

Pure rules live in [`services/inventory/domain.py`](services/inventory/domain.py) (stock aggregation per warehouse, reorder threshold, allowed ingredient units). HTTP handlers in [`services/inventory/main.py`](services/inventory/main.py) call into `domain` for validation and summaries.

**New endpoint:** `GET /ingredients/{ingredient_id}/stock-summary` — total quantity across warehouses, per-warehouse breakdown, and `is_below_reorder` vs the ingredient’s `ReorderLevel`.

Ingredient `unit` values are normalized to one of: `kg`, `g`, `l`, `ml`, `pcs` (see domain).

## Environment

Copy [`.env.example`](.env.example) → `.env`. For Docker Compose, [`docker-compose.yml`](docker-compose.yml) maps host `.env` into the container via `${VAR:-…}` placeholders (see file header).

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

Local:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn services.inventory.main:app --host 127.0.0.1 --port 8001
```

OpenAPI: `http://127.0.0.1:8001/docs`

## Tests and lint (local)

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
pytest tests/ -v --tb=short
```

- `tests/test_smoke.py` — app wiring / OpenAPI (no DB).
- `tests/test_domain.py` — unit tests for `services.inventory.domain`.

## CI (Azure Pipelines)

Pipeline definition: [`azure-pipelines.yml`](azure-pipelines.yml). On push or PR to `main` it runs **Ruff** then **Pytest**. In Azure DevOps, create a pipeline that uses this YAML from the repo root. Optional pipeline variables mirror `.env.example` if you later add database integration tests.
