class CoverageEngine:
    def calculate(self, trace, model):
        processes_covered = []
        policies_exercised = []
        constraints_exercised = []
        
        for event in trace.events:
            event_type = type(event).__name__
            if event_type == "PolicyApplied":
                policies_exercised.append(event.policy_id)
            elif event_type == "ConstraintEvaluated":
                constraints_exercised.append(event.constraint_id)
            elif event_type == "ProcessEvaluated":
                processes_covered.append(event.process_id)
                
        return {
            "processes_covered": processes_covered,
            "policies_exercised": policies_exercised,
            "constraints_exercised": constraints_exercised,
            "regulations_evaluated": [],
            "personas_invoked": [],
            "decisions_used": [],
            "actions_executed": [],
            "transitions_tested": [],
            "events_triggered": []
        }
