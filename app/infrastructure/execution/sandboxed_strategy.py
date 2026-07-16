import asyncio
import concurrent.futures
import logging
from collections.abc import Callable
from typing import Any

from app.infrastructure.execution.strategy import (
    ExecutionContext as StrategyExecutionContext,
    ExecutionResult,
    ExecutionStrategy,
    IExecutionStrategy,
)
from app.domain.security.models import SandboxPolicy
from app.domain.security.interfaces import ISandboxPolicyEnforcer, IAuditPublisher
from app.shared.events.models import SecurityEvent, AuditCategory
from app.infrastructure.security.sandbox import PythonAuditHookEnforcer
from dataclasses import asdict
import uuid

logger = logging.getLogger(__name__)

def _sandboxed_execute_wrapper(policy: SandboxPolicy | None, callable_fn: Callable[..., Any], args: tuple, kwargs: dict) -> Any:
    """
    Wrapper to enforce sandbox policies before executing the callable inside the subprocess.
    """
    if policy is not None:
        # We instantiate the default enforcer if a policy is provided. 
        # (This is kept decoupled; stronger implementations could replace the strategy entirely)
        enforcer = PythonAuditHookEnforcer()
        enforcer.enforce(policy)
        
    return callable_fn(*args, **kwargs)

class SandboxedExecutionStrategy(IExecutionStrategy):
    """
    Executes callables in a separate process with a SandboxPolicy enforced.
    Serves as the foundational 'Sandboxed Execution Environment' combining
    process isolation and runtime policy enforcement.
    """
    
    def __init__(self, audit_publisher: IAuditPublisher | None = None):
        self._audit_publisher = audit_publisher
        
    def _emit_audit(self, context: StrategyExecutionContext, action: str, result: str, metadata: dict | None = None, severity: str = "INFO") -> None:
        if not self._audit_publisher:
            return
            
        ctx_dict = None
        # We try to extract info from the generic ExecutionContext if it's there
        if hasattr(context, "sandbox_policy") and context.sandbox_policy:
            ctx_dict = {"sandbox_policy": asdict(context.sandbox_policy)}
            
        event = SecurityEvent(
            correlation_id=str(context.lifecycle_id) if getattr(context, "lifecycle_id", None) else str(uuid.uuid4()),
            category=AuditCategory.SANDBOX,
            action=action,
            result=result,
            execution_context=ctx_dict,
            metadata=metadata,
            severity=severity
        )
        self._audit_publisher.publish_audit(event)
    
    @property
    def strategy_type(self) -> ExecutionStrategy:
        return ExecutionStrategy.SANDBOXED

    async def execute(
        self, callable_fn: Callable[..., Any], context: StrategyExecutionContext, *args: Any, **kwargs: Any
    ) -> ExecutionResult:
        loop = asyncio.get_running_loop()
        policy = context.sandbox_policy
        
        logger.info("sandbox_execution_started", extra={"strategy": "subprocess_sandbox", "lifecycle_id": context.lifecycle_id})
        self._emit_audit(context, "EXECUTION_STARTED", "SUCCESS")
        
        try:
            # We use max_workers=1 to ensure each callable gets a fresh isolated process if we were to recreate the pool
            # For concurrent.futures, ProcessPoolExecutor creates a fresh pool here.
            with concurrent.futures.ProcessPoolExecutor(max_workers=1) as pool:
                # Resolve timeout
                timeout_s = context.timeout_seconds
                if policy and policy.max_execution_time_seconds:
                    timeout_s = min(timeout_s, float(policy.max_execution_time_seconds))
                    
                future = loop.run_in_executor(pool, _sandboxed_execute_wrapper, policy, callable_fn, args, kwargs)
                result = await asyncio.wait_for(future, timeout=timeout_s)
                
            logger.info("sandbox_execution_completed", extra={"lifecycle_id": context.lifecycle_id})
            self._emit_audit(context, "EXECUTION_COMPLETED", "SUCCESS")
            return ExecutionResult(
                success=True,
                result=result,
                lifecycle_id=context.lifecycle_id
            )
            
        except asyncio.TimeoutError:
            logger.warning("sandbox_execution_timeout", extra={"lifecycle_id": context.lifecycle_id, "timeout_s": context.timeout_seconds})
            self._emit_audit(context, "EXECUTION_TIMEOUT", "FAILURE", metadata={"timeout_s": context.timeout_seconds}, severity="WARNING")
            return ExecutionResult(
                success=False,
                error=f"Execution timed out after {context.timeout_seconds}s",
                lifecycle_id=context.lifecycle_id
            )
        except concurrent.futures.process.BrokenProcessPool:
            # Typically happens if the subprocess is killed externally or crashes hard
            logger.error("sandbox_execution_blocked", extra={"lifecycle_id": context.lifecycle_id, "reason": "Broken process pool (hard crash)"})
            self._emit_audit(context, "EXECUTION_CRASHED", "FAILURE", metadata={"reason": "Broken process pool"}, severity="ERROR")
            return ExecutionResult(
                success=False,
                error="Process pool broken (hard crash)",
                lifecycle_id=context.lifecycle_id
            )
        except Exception as e:
            # If the exception came from our audit hook, it's typically a PermissionError
            error_msg = str(e)
            if "Sandbox policy violation" in error_msg:
                logger.warning("sandbox_policy_violation", extra={"lifecycle_id": context.lifecycle_id, "error": error_msg})
                self._emit_audit(context, "POLICY_VIOLATION", "FAILURE", metadata={"error": error_msg}, severity="CRITICAL")
            else:
                logger.warning("sandbox_execution_blocked", extra={"lifecycle_id": context.lifecycle_id, "error": error_msg})
                self._emit_audit(context, "EXECUTION_BLOCKED", "FAILURE", metadata={"error": error_msg}, severity="WARNING")
                
            return ExecutionResult(
                success=False,
                error=error_msg,
                lifecycle_id=context.lifecycle_id
            )
