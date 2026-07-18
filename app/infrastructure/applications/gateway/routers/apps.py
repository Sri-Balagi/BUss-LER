from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from app.bootstrap.container import get_container
from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.domain.applications.registry.models import ApplicationMetadata

router = APIRouter(prefix="/apps", tags=["Applications"])

def get_registry() -> IApplicationRegistry:
    container = get_container()
    return container.resolve(IApplicationRegistry)

@router.get("/", response_model=List[ApplicationMetadata])
async def list_applications(registry: IApplicationRegistry = Depends(get_registry)):
    """Discover all registered cognitive applications."""
    return registry.get_all_metadata()

@router.get("/{app_id}", response_model=ApplicationMetadata)
async def get_application(app_id: str, registry: IApplicationRegistry = Depends(get_registry)):
    """Get metadata for a specific application."""
    app = registry.resolve(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
    return app.metadata()

@router.post("/{app_id}/jobs")
async def submit_job(app_id: str, context_data: dict, request: Request, registry: IApplicationRegistry = Depends(get_registry)):
    """Submit a background job to an asynchronous application."""
    app = registry.resolve(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
        
    if not hasattr(app, 'submit_job'):
        raise HTTPException(status_code=400, detail=f"Application {app_id} does not support background jobs")
        
    # Inject tracing and tenant from request state
    context_data['trace_id'] = getattr(request.state, 'trace_id', None)
    context_data['span_id'] = getattr(request.state, 'span_id', None)
    
    if 'user_id' not in context_data:
        context_data['user_id'] = getattr(request.state, 'user_id', 'anonymous')
    if 'tenant_id' not in context_data:
        context_data['tenant_id'] = getattr(request.state, 'tenant_id', 'default-tenant')

    # Context validation based on app_id
    if app_id == "bizos.worker.v1":
        from app.domain.applications.context.models import WorkerContext
        context = WorkerContext(**context_data)
    elif app_id == "bizos.insights.v1":
        from app.domain.applications.insights.models import InsightContext
        context = InsightContext(**context_data)
    elif app_id == "bizos.trigger.v1":
        from app.domain.applications.trigger.models import TriggerContext
        context = TriggerContext(**context_data)
    else:
        from app.domain.applications.context.models import ApplicationContext
        context = ApplicationContext(**context_data)
    
    job_id = await app.submit_job(context)
    return {"job_id": job_id}

@router.get("/{app_id}/jobs/{job_id}")
async def get_job_status(app_id: str, job_id: str, registry: IApplicationRegistry = Depends(get_registry)):
    """Retrieve the status of a background job."""
    app = registry.resolve(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"Application {app_id} not found")
        
    if not hasattr(app, 'get_job_status'):
        raise HTTPException(status_code=400, detail=f"Application {app_id} does not support background jobs")
        
    try:
        job_record = await app.get_job_status(job_id)
        return job_record
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
