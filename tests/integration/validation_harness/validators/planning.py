def validate(trace, scenario):
    if trace.errors:
        return False, f"Errors occurred during execution: {trace.errors[0]}"
        
    event_types = [type(e).__name__ for e in trace.events]
    
    if scenario.expected_outcome == "Success":
        if "PlanGenerated" not in event_types:
            return False, "Expected PlanGenerated event but it was missing"
    else:
        # Expected failure
        if "PlanValidationFailed" not in event_types and "PlanGenerationFailed" not in event_types:
            # For now, deterministic provider doesn't fail, so this will highlight the Cognitive Model Gap.
            return False, f"Expected validation failure for {scenario.category}, but plan generated successfully"
            
    return True, "Planning trace passed"