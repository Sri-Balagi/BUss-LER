import os
from unittest.mock import MagicMock, patch

from app.shell.commands.devex_cmds import (
    handle_create_app,
    handle_create_plugin,
    register_devex_commands,
)
from app.shell.dispatcher import ShellDispatcher


@patch("app.shell.commands.devex_cmds.Scaffolder")
def test_handle_create_app(MockScaffolder):
    client = MagicMock()
    formatter = MagicMock()

    # Missing args
    assert handle_create_app(client, formatter, []) == 1
    formatter.print_error.assert_called_once()
    formatter.reset_mock()

    # Success
    mock_instance = MockScaffolder.return_value
    assert handle_create_app(client, formatter, ["myapp"]) == 0
    mock_instance.create_app.assert_called_once_with("myapp", os.path.join(os.getcwd(), "myapp"))

    # Exception
    mock_instance.create_app.side_effect = Exception("Test error")
    assert handle_create_app(client, formatter, ["myapp"]) == 1
    formatter.print_error.assert_called_once()

@patch("app.shell.commands.devex_cmds.Scaffolder")
def test_handle_create_plugin(MockScaffolder):
    client = MagicMock()
    formatter = MagicMock()

    # Missing args
    assert handle_create_plugin(client, formatter, []) == 1
    formatter.print_error.assert_called_once()
    formatter.reset_mock()

    # Success
    mock_instance = MockScaffolder.return_value
    assert handle_create_plugin(client, formatter, ["myplugin"]) == 0
    mock_instance.create_plugin.assert_called_once_with("myplugin", os.path.join(os.getcwd(), "myplugin"))

    # Exception
    mock_instance.create_plugin.side_effect = Exception("Test error")
    assert handle_create_plugin(client, formatter, ["myplugin"]) == 1
    formatter.print_error.assert_called_once()

def test_register_devex_commands():
    dispatcher = ShellDispatcher(MagicMock(), MagicMock())
    register_devex_commands(dispatcher)
    assert "create-app" in dispatcher._commands
    assert "create-plugin" in dispatcher._commands
