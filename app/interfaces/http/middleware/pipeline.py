from fastapi import FastAPI

from app.interfaces.http.middleware.auth import AuthMiddleware
from app.interfaces.http.middleware.context import RequestContextMiddleware
from app.interfaces.http.middleware.idempotency import IdempotencyMiddleware
from app.interfaces.http.middleware.lifecycle import ApiLifecycleMiddleware
from app.interfaces.http.middleware.rate_limiter import RateLimiterMiddleware
from app.interfaces.http.middleware.tenant import TenantResolutionMiddleware

# FastAPI middleware is executed in the REVERSE order of how they are added.
# So the last middleware added is the FIRST one to run (closest to the client).
#
# Our target pipeline (Outer to Inner):
# 1. RequestContext (Tracing)
# 2. RateLimiter
# 3. Auth
# 4. TenantResolution
# 5. Idempotency
# 6. ApiLifecycle


def register_gateway_pipeline(app: FastAPI) -> None:
    """
    Registers the strict request pipeline for the API Gateway.
    """
    # 6. ApiLifecycle (Innermost, closest to the router)
    app.add_middleware(ApiLifecycleMiddleware)

    # 5. Idempotency (Safeguards against retries)
    app.add_middleware(IdempotencyMiddleware)
    
    # 4. Tenant Resolution (Runs after auth so it can extract tenant from auth claims)
    app.add_middleware(TenantResolutionMiddleware)

    # 3. Authentication (Validates tokens/keys)
    app.add_middleware(AuthMiddleware)

    # 2. Rate Limiting (Drops spam quickly)
    app.add_middleware(RateLimiterMiddleware)

    # 1. Request Context & Tracing (Outermost, starts the timer and traces)
    # Note: If RequestIDMiddleware is already registered in main.py, 
    # we should replace it with this one.
    app.add_middleware(RequestContextMiddleware)
