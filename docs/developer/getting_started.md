# Developer Guide — Getting Started

**BizOS v6.0.0**

## Prerequisites

- Python 3.12+, uv (latest), Docker, Git

## Environment Setup

    uv sync
    cp .env.example .env

Required env vars: SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY, QDRANT_HOST, QDRANT_PORT

## Running

    docker-compose up -d
    uv run uvicorn app.main:app --reload

## Testing

    uv run pytest
    uv run pytest tests/runtime/
    uv run pytest --cov=app --cov-report=html

## Code Quality

    uv run ruff check app/ tests/
    uv run ruff check app/ tests/ --fix

## Architectural Rules

NEVER: Import from intelligence/ inside runtime/, or from runtime/ inside intelligence/ except via runtime_bridge/.
ALWAYS: Place tests beside the production code they test. Use TYPE_CHECKING for forward references.

## Layout

    app/runtime/         # M5 FROZEN
    app/intelligence/    # M6 FROZEN
    app/infrastructure/  # Extend via abstraction
    app/interfaces/      # HTTP API
    app/platform/        # Config and DI
    app/shared/          # Universal primitives only
