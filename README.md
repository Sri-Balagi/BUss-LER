# BizOS

BizOS is an AI Operating System for Entities. It understands an entity, builds a digital twin of it, and helps it achieve its goals through planning, reasoning, memory, simulation, and autonomous execution.

> **Current Status**: Milestone 0 — Core foundations, database connections, and domain models.

## Project Structure

- `app/`: FastAPI application code.
  - `api/`: API routers and endpoints.
  - `models/`: Pydantic schemas and enums (Business Foundation Model).
  - `services/`: Wrappers for external services (Supabase, Qdrant, Gemini).
- `tests/`: Pytest test suite.

## Installation

The project uses `uv` for dependency management.

1. Ensure Python 3.12+ is installed.
2. Install `uv` if you haven't already.
3. Install dependencies:

```bash
uv sync
```

Or using standard pip:

```bash
pip install -e ".[dev]"
```

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Fill in the required values in `.env`:
   - `SUPABASE_URL` and `SUPABASE_KEY` (from your Supabase project)
   - `GEMINI_API_KEY` (from Google AI Studio)

## Running Infrastructure

Qdrant runs locally via Docker. To start it:

```bash
docker-compose up -d
```

## Running the Application

To start the FastAPI development server:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Check the health endpoint at `http://localhost:8000/api/v1/health`.
API documentation is available at `http://localhost:8000/docs`.

## Running Tests

To run the test suite:

```bash
uv run pytest
```
