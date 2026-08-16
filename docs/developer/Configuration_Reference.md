# BizOS Memory Engine Configuration Reference

This document provides a comprehensive audit of all configuration variables for the BizOS Memory Engine. Configuration is managed via Pydantic `BaseSettings` (`app/config.py`).

## Core Configuration Matrix

| Variable Name | Required | Default | Description | Failure Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `SUPABASE_URL` | Yes | - | URL of the Supabase instance. | `ValidationError` on startup. |
| `SUPABASE_KEY` | Yes | - | API or service role key for Supabase. | `ValidationError` on startup. |
| `QDRANT_HOST` | No | `"localhost"` | Hostname for Qdrant vector DB. | Uses local default; API fails gracefully later if Qdrant is unreachable. |
| `QDRANT_PORT` | No | `6333` | REST port for Qdrant. | - |
| `QDRANT_COLLECTION` | No | `"memories"` | Default Qdrant collection name. | - |
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key. | `ValidationError` on startup. |
| `APP_ENV` | No | `"development"` | Application environment. | - |
| `LOG_LEVEL` | No | `"INFO"` | Standard Python logging levels. | Invalid format falls back to default safely. |

## Feature Flags

| Variable Name | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `ENABLE_BACKGROUND_PROCESSING`| No | `True` | If disabled, the API routes events synchronously (or fails gracefully). |
| `ENABLE_AI_SUMMARIZATION` | No | `True` | Controls auto-summarization on creation. |
| `ENABLE_VECTOR_STORAGE` | No | `True` | Toggles whether vectors are generated and synced. |

## Invalid Configuration Handling
By extending `pydantic-settings`, the backend process validates the environment matrix *synchronously before boot*. If a required variable (`SUPABASE_KEY`, `GEMINI_API_KEY`) is missing, FastAPI will immediately terminate with a clear `pydantic.ValidationError` stack trace describing exactly which variable is missing, preventing degraded runtime surprises.
