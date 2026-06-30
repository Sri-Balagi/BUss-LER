# =============================================================================
# BizOS v6.0.0 — Production Dockerfile
# Multi-stage build: builder → runtime
# =============================================================================

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv==0.5.26

# Copy dependency files first (cache layer)
COPY pyproject.toml uv.lock ./

# Install production dependencies only (no dev extras)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY app/ ./app/

# ── Stage 2: Production Runtime ───────────────────────────────────────────────
FROM python:3.12-slim AS production

LABEL org.opencontainers.image.title="BizOS"
LABEL org.opencontainers.image.description="AI Operating System for Entities"
LABEL org.opencontainers.image.version="6.0.0"
LABEL org.opencontainers.image.source="https://github.com/your-org/bizos"
LABEL org.opencontainers.image.licenses="MIT"

# Security: non-root user
RUN groupadd -r bizos && useradd -r -g bizos -d /app -s /sbin/nologin bizos

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/app /app/app

# Set environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    APP_DEBUG=false \
    LOG_LEVEL=INFO

# Security: switch to non-root
USER bizos

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Production server: uvicorn with multiple workers
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--no-access-log", \
     "--proxy-headers"]
