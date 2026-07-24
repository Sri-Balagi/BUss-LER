import os
import tempfile
from unittest.mock import MagicMock

from app.shell.bizshell import BizShell


def test_run_script():
    shell = BizShell()

    # Mock execute_command to simulate execution
    shell.execute_command = MagicMock(return_value=0)

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("ls-registry tools\n")
        f.write("# a comment\n")
        f.write("ps\n")
        temp_path = f.name

    try:
        exit_code = shell.run_script(temp_path)
        assert exit_code == 0
        assert shell.execute_command.call_count == 2
    finally:
        os.remove(temp_path)
