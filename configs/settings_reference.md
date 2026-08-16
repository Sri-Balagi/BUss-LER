# BizOS Settings Reference

Complete documentation for all environment variables.
See `.env.example` for a template.

## Required Variables

| Variable | Type | Description |
|----------|------|-------------|
| `SUPABASE_URL` | URL | Supabase project URL (`https://xxx.supabase.co`) |
| `SUPABASE_KEY` | String | Supabase anon or service key |
| `GEMINI_API_KEY` | String | Google Gemini API key |

## Qdrant

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `QDRANT_HOST` | String | `localhost` | Qdrant host |
| `QDRANT_PORT` | Integer | `6333` | Qdrant HTTP port |
| `QDRANT_COLLECTION` | String | `memories` | Default collection name |
| `QDRANT_VECTOR_SIZE` | Integer | `768` | Embedding dimensions |
| `QDRANT_DISTANCE_METRIC` | String | `Cosine` | Distance metric: Cosine, Dot, Euclid |

## Application

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_ENV` | Enum | `development` | `development`, `test`, `staging`, `production` |
| `APP_DEBUG` | Boolean | `false` | Enable debug mode (shows /docs, /redoc) |
| `LOG_LEVEL` | Enum | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

## Security

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CORS_ORIGINS` | JSON Array | `["*"]` | Allowed CORS origins. Restrict in production. |

## Observability

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OTEL_ENABLED` | Boolean | `false` | Enable OpenTelemetry tracing |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | URL | None | OTLP collector endpoint |

## Feature Flags

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_BACKGROUND_PROCESSING` | Boolean | `true` | Enable async background tasks |
| `ENABLE_AI_SUMMARIZATION` | Boolean | `true` | Enable AI-powered summarization |
| `ENABLE_VECTOR_STORAGE` | Boolean | `true` | Enable Qdrant vector storage |

## Operational

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REQUEST_TIMEOUT_SECONDS` | Float | `30.0` | Global request timeout |

## Production Checklist

- [ ] `APP_ENV=production`
- [ ] `APP_DEBUG=false`
- [ ] `CORS_ORIGINS` restricted to your domain
- [ ] `SUPABASE_KEY` uses service role key (not anon)
- [ ] `/metrics` endpoint protected at network level (not exposed publicly)
- [ ] `OTEL_ENABLED=true` if using distributed tracing
