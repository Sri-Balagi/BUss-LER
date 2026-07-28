
from tests.integration.validation_harness.models import ValidationScenario
from app.domain.planning.models import Goal

SCENARIOS = []

# Generate 40 scenarios for Accounting
for i in range(1, 41):
    cat = "Happy Path" if i < 10 else ("Policy Violations" if i < 20 else ("Constraint Violations" if i < 30 else "Edge Cases"))
    
    # DeterministicPlanner triggers validation failure if 'invalid' is in the description
    if cat == "Happy Path":
        desc = f"Execute Month-End Financial Close for task {i}"
    elif cat == "Policy Violations":
        desc = f"Execute invalid task {i} causing GAAP Compliance and Revenue Recognition (policy violations)"
    elif cat == "Constraint Violations":
        desc = f"Execute invalid task {i} causing Balance Sheet Equation (Assets = Liabilities + Equity) (constraint violations)"
    else:
        desc = f"Execute invalid task {i} for {cat}"
    
    SCENARIOS.append(
        ValidationScenario(
            module_name="accounting",
            scenario_id=f"acc_{cat.replace(' ', '_').lower()}_{i:03d}",
            category=cat,
            description=desc,
            initial_business_context={"load": i},
            memory_seed={},
            digital_twin_seed={},
            input_request=Goal(description=desc),
            expected_outcome="Success" if cat == "Happy Path" else "Validation Failure"
        )
    )
