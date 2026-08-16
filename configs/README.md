# configs/

This directory contains environment-specific configuration files.

## docker-compose.yml

Starts a local Qdrant vector store instance for development and testing.

Usage:
    docker-compose up -d        # start in background
    docker-compose down         # stop and remove containers

Qdrant UI: http://localhost:6333/dashboard

## Environment Variables

Application configuration is managed via `.env` in the repository root.
Copy `.env.example` to `.env` and fill in your credentials.

Required variables:
- SUPABASE_URL
- SUPABASE_KEY
- GEMINI_API_KEY
- QDRANT_HOST (default: localhost)
- QDRANT_PORT (default: 6333)
