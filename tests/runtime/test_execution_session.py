from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.session.cancellation import CancellationToken
from app.runtime.session.execution_session import ExecutionSession
from app.runtime.session.runtime_identity import RuntimeIdentity
from app.runtime.session.working_memory import WorkingMemory


def test_execution_session_assembly():
    identity = RuntimeIdentity()
    memory = WorkingMemory()
    budget = ExecutionBudget()
    cancel_token = CancellationToken()

    session = ExecutionSession(
        identity=identity,
        memory=memory,
        budget=budget,
        cancellation_token=cancel_token,
        enterprise_context_version="v2",
    )

    assert session.identity.session_id == identity.session_id
    assert session.enterprise_context_version == "v2"
    assert session.budget.max_tokens == 128000
    assert not session.cancellation_token.is_cancelled()
