from app.shell.dispatcher import ShellDispatcher
from app.shell.formatter import ShellFormatter
from unittest.mock import MagicMock

def test_shell_dispatcher_register_and_dispatch():
    formatter = ShellFormatter(use_json=False)
    client = MagicMock()
    dispatcher = ShellDispatcher(client, formatter)
    
    # Mock command handler
    def mock_handler(c, f, args):
        if args and args[0] == "fail":
            return 1
        return 0
        
    dispatcher.register_command("test-cmd", mock_handler)
    
    # Dispatch success
    exit_code = dispatcher.dispatch("test-cmd", [])
    assert exit_code == 0
    
    # Dispatch fail
    exit_code = dispatcher.dispatch("test-cmd", ["fail"])
    assert exit_code == 1
    
    # Command not found
    exit_code = dispatcher.dispatch("unknown", [])
    assert exit_code == 127
