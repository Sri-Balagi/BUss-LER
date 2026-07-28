import asyncio
import importlib
from .harness import RuntimeValidationHarness
from .reporting import ReportingEngine
from .coverage import CoverageEngine
from .validators import retrieval, planning, reasoning, workflow, memory, digital_twin, multi_agent

async def run_scenarios(module_name: str):
    harness = RuntimeValidationHarness()
    reporter = ReportingEngine()
    coverage = CoverageEngine()
    
    # Load scenarios dynamically
    try:
        mod = importlib.import_module(f"tests.integration.validation_harness.scenarios.{module_name}.scenarios")
        scenarios = mod.SCENARIOS
    except ImportError:
        print(f"No scenarios found for {module_name}")
        return
        
    for scenario in scenarios:
        print(f"Executing: {scenario.scenario_id}")
        trace = await harness.execute_scenario(scenario)
        
        # Validate
        v_results = {
            "retrieval": retrieval.validate(trace, scenario),
            "planning": planning.validate(trace, scenario),
            "reasoning": reasoning.validate(trace, scenario),
            "workflow": workflow.validate(trace, scenario),
            "memory": memory.validate(trace, scenario),
            "digital_twin": digital_twin.validate(trace, scenario),
            "multi_agent": multi_agent.validate(trace, scenario)
        }
        
        # Coverage
        cov = coverage.calculate(trace, None)
        
        reporter.generate_report(scenario, trace, v_results, cov)
        
    reporter.generate_manifest(module_name)

if __name__ == "__main__":
    asyncio.run(run_scenarios("healthcare"))
