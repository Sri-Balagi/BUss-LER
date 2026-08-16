from unittest.mock import MagicMock

from app.shell.commands.workflow_cmds import handle_ps, handle_workflow, register_workflow_commands
from app.shell.dispatcher import ShellDispatcher


def test_handle_ps_empty():
    client = MagicMock()
    formatter = MagicMock()

    client.list_active_workflows.return_value = []

    assert handle_ps(client, formatter, []) == 0
    formatter.print_success.assert_called_once()

def test_handle_ps_items():
    client = MagicMock()
    formatter = MagicMock()

    client.list_active_workflows.return_value = [
        {"id": "1", "status": "RUNNING", "started": "Now"}
    ]

    assert handle_ps(client, formatter, []) == 0
    formatter.print_table.assert_called_once()

def test_handle_ps_error():
    client = MagicMock()
    formatter = MagicMock()

    client.list_active_workflows.side_effect = Exception("Test Error")

    assert handle_ps(client, formatter, []) == 1
    formatter.print_error.assert_called_once()

def test_handle_workflow_no_args():
    client = MagicMock()
    formatter = MagicMock()

    assert handle_workflow(client, formatter, []) == 1
    formatter.print_error.assert_called_once()

def test_handle_workflow_ps():
    client = MagicMock()
    formatter = MagicMock()

    client.list_active_workflows.return_value = []

    assert handle_workflow(client, formatter, ["ps"]) == 0
    formatter.print_success.assert_called_once()

def test_handle_workflow_kill():
    client = MagicMock()
    formatter = MagicMock()

    assert handle_workflow(client, formatter, ["kill"]) == 1
    formatter.print_error.assert_called_once()

def test_handle_workflow_unknown():
    client = MagicMock()
    formatter = MagicMock()

    assert handle_workflow(client, formatter, ["unknown"]) == 1
    formatter.print_error.assert_called_once()

def test_register_workflow_commands():
    dispatcher = ShellDispatcher(MagicMock(), MagicMock())
    register_workflow_commands(dispatcher)

    assert "ps" in dispatcher._commands
    assert "workflow" in dispatcher._commands
