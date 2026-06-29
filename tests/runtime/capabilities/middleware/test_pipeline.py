import pytest
from uuid import uuid4
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult, ExecutionStatus
from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.middleware.context import MiddlewareContext
from app.runtime.capabilities.middleware.interfaces import IMiddleware
from app.runtime.capabilities.middleware.decision import MiddlewareDecision
from app.runtime.capabilities.middleware.pipeline import CapabilityPipeline
from app.runtime.capabilities.middleware.validation import ValidationMiddleware
from app.runtime.capabilities.middleware.permissions import PermissionMiddleware
from app.runtime.capabilities.middleware.policies import PolicyMiddleware
from app.runtime.capabilities.middleware.tracing import TracingMiddleware
from app.runtime.capabilities.middleware.logging import LoggingMiddleware

class OrderingMiddleware(IMiddleware):
    def __init__(self, name: str, call_log: list):
        self.name = name
        self.call_log = call_log
        
    async def before_execution(self, req, cap_ctx, mw_ctx):
        self.call_log.append(f"{self.name}_before")
        return MiddlewareDecision.ALLOW

    async def after_execution(self, req, cap_ctx, mw_ctx, result):
        self.call_log.append(f"{self.name}_after")
        return result

    async def on_exception(self, req, cap_ctx, mw_ctx, exc):
        self.call_log.append(f"{self.name}_exc")
        return MiddlewareDecision.ALLOW

class ShortCircuitMiddleware(IMiddleware):
    async def before_execution(self, req, cap_ctx, mw_ctx):
        return MiddlewareDecision.SHORT_CIRCUIT
        
    async def after_execution(self, req, cap_ctx, mw_ctx, result):
        return result
        
    async def on_exception(self, req, cap_ctx, mw_ctx, exc):
        return MiddlewareDecision.ALLOW

@pytest.fixture
def mock_request():
    return CapabilityRequest(
        capability_id="test_cap",
        operation="test",
        arguments={},
        caller_id="test_caller",
        trace_id=uuid4()
    )

@pytest.fixture
def mock_context():
    return CapabilityContext()

async def mock_executor(req, ctx):
    return CapabilityResult(status=ExecutionStatus.SUCCESS, outputs={"executed": True})

async def mock_failing_executor(req, ctx):
    raise ValueError("Test error")

@pytest.mark.anyio
async def test_pipeline_ordering(mock_request, mock_context):
    call_log = []
    pipeline = CapabilityPipeline([
        OrderingMiddleware("mw1", call_log),
        OrderingMiddleware("mw2", call_log),
        OrderingMiddleware("mw3", call_log)
    ])
    
    async def instrumented_executor(req, ctx):
        call_log.append("executor")
        return await mock_executor(req, ctx)
        
    res = await pipeline.execute(mock_request, mock_context, instrumented_executor)
    
    assert res.status == ExecutionStatus.SUCCESS
    # before is in order, after is in reverse order
    assert call_log == [
        "mw1_before", "mw2_before", "mw3_before", 
        "executor", 
        "mw3_after", "mw2_after", "mw1_after"
    ]

@pytest.mark.anyio
async def test_pipeline_on_exception_ordering(mock_request, mock_context):
    call_log = []
    pipeline = CapabilityPipeline([
        OrderingMiddleware("mw1", call_log),
        OrderingMiddleware("mw2", call_log)
    ])
    
    res = await pipeline.execute(mock_request, mock_context, mock_failing_executor)
    
    assert res.status == ExecutionStatus.FAILURE
    assert res.errors == ["Test error"]
    assert call_log == [
        "mw1_before", "mw2_before",
        "mw2_exc", "mw1_exc"
    ]

@pytest.mark.anyio
async def test_pipeline_short_circuit(mock_request, mock_context):
    call_log = []
    pipeline = CapabilityPipeline([
        OrderingMiddleware("mw1", call_log),
        ShortCircuitMiddleware(),
        OrderingMiddleware("mw3", call_log)
    ])
    
    async def instrumented_executor(req, ctx):
        call_log.append("executor")
        return await mock_executor(req, ctx)
        
    res = await pipeline.execute(mock_request, mock_context, instrumented_executor)
    
    assert res.status == ExecutionStatus.SUCCESS
    assert "short-circuited" in res.warnings[0]
    
    # executor should NOT run, mw3_before should NOT run.
    assert call_log == ["mw1_before"]

@pytest.mark.anyio
async def test_validation_middleware(mock_request, mock_context):
    pipeline = CapabilityPipeline([ValidationMiddleware()])
    
    # valid request
    res = await pipeline.execute(mock_request, mock_context, mock_executor)
    assert res.status == ExecutionStatus.SUCCESS
    
    # invalid request
    bad_req = CapabilityRequest(capability_id="x", operation="x", arguments={})
    # bad_req.caller_id is None
    res2 = await pipeline.execute(bad_req, mock_context, mock_executor)
    assert res2.status == ExecutionStatus.FAILURE
    assert "ValidationMiddleware" in res2.errors[0]
    assert res2.validation_results["validation_error"] == "Missing caller_id"

@pytest.mark.anyio
async def test_permission_middleware(mock_request, mock_context):
    pipeline = CapabilityPipeline([PermissionMiddleware()])
    
    res = await pipeline.execute(mock_request, mock_context, mock_executor)
    assert res.status == ExecutionStatus.SUCCESS
    
    bad_req = mock_request.model_copy(update={"execution_metadata": {"force_deny": True}})
    res2 = await pipeline.execute(bad_req, mock_context, mock_executor)
    assert res2.status == ExecutionStatus.FAILURE
    assert "PermissionMiddleware" in res2.errors[0]
    assert res2.validation_results["permission_error"] == "Forced deny"

@pytest.mark.anyio
async def test_tracing_middleware(mock_request, mock_context):
    pipeline = CapabilityPipeline([TracingMiddleware()])
    
    res = await pipeline.execute(mock_request, mock_context, mock_executor)
    assert res.status == ExecutionStatus.SUCCESS
    assert res.execution_trace_id == mock_request.trace_id

@pytest.mark.anyio
async def test_full_pipeline_integration(mock_request, mock_context):
    pipeline = CapabilityPipeline([
        TracingMiddleware(),
        LoggingMiddleware(),
        ValidationMiddleware(),
        PermissionMiddleware(),
        PolicyMiddleware()
    ])
    
    res = await pipeline.execute(mock_request, mock_context, mock_executor)
    assert res.status == ExecutionStatus.SUCCESS
    assert res.execution_trace_id == mock_request.trace_id
