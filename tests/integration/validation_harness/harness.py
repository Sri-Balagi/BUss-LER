import time
import asyncio
from typing import Optional
from app.bootstrap.container import Container, build_container, reset_container_for_testing
from app.application.intelligence.kernel import IntelligenceKernel
from .models import ValidationScenario, ValidationTrace
from .trace_builder import ValidationTraceBuilder

class RuntimeValidationHarness:
    def __init__(self):
        reset_container_for_testing()
        self.container = build_container()
        self.kernel = self.container.resolve(IntelligenceKernel)
        
    def load_module(self, module_name: str):
        # The intelligence kernel or module registry would load it here
        # For validation, we ensure the module is registered.
        pass
        
    async def execute_scenario(self, scenario: ValidationScenario) -> ValidationTrace:
        self.load_module(scenario.module_name)
        
        builder = ValidationTraceBuilder(scenario.scenario_id)
        
        async def _handle_event(event):
            builder.capture_event(event)

        # Hook into kernel's event bus
        bus = None
        if hasattr(self.kernel, "event_router"):
            bus = getattr(self.kernel.event_router, "_event_bus", None)
            if bus:
                bus.subscribe("*", _handle_event)
            
        start_time = time.time()
        try:
            # Execute
            from app.application.planning.service import PlanningEngineService
            from app.domain.planning.models import PlanningContext
            from app.application.reasoning.service import ReasoningEngineService
            from app.domain.reasoning.models import ReasoningQuery
            import uuid
            
            planning_engine = self.container.resolve(PlanningEngineService)
            reasoning_engine = self.container.resolve(ReasoningEngineService)
            
            tenant_id = uuid.uuid4()
            session_id = uuid.uuid4()
            correlation_id = str(uuid.uuid4())
            
            bkm = None
            reasoning_response = None
            
            import importlib
            try:
                mod = importlib.import_module(f"app.modules.{scenario.module_name}.ai.cognition")
                bkm = getattr(mod, f"{scenario.module_name.upper()}_KNOWLEDGE_MODEL")
                
                # --- ACTUAL REASONING ENGINE EXECUTION ---
                # Build context and query to execute real reasoning
                from app.domain.intelligence.context import IntelligenceContext
                
                intel_ctx = IntelligenceContext(
                    tenant_id=tenant_id,
                    user_id=uuid.uuid4(),
                    session_id=session_id,
                    correlation_id=correlation_id,
                    permissions=["*"]
                )
                
                query = ReasoningQuery(
                    query_text=scenario.input_request.description,
                    context_data={"active_knowledge_model": bkm}
                )
                
                reasoning_response = await reasoning_engine.execute_reasoning(intel_ctx, query)
                
            except Exception as e:
                print(f"Reasoning error for {scenario.module_name}: {e}")
                pass
            
            ctx = PlanningContext(
                tenant_id=tenant_id,
                session_id=session_id,
                correlation_id=correlation_id,
                active_knowledge_model=bkm,
                reasoning_result=reasoning_response
            )
            
            await planning_engine.create_plan(ctx, scenario.input_request)
            
            # Flush event bus tasks
            import asyncio
            await asyncio.sleep(0.05)
            
        except Exception as e:
            builder.set_error(str(e))
        finally:
            if bus:
                bus.unsubscribe("*", _handle_event)
            
        duration = time.time() - start_time
        return builder.finalize(duration)
