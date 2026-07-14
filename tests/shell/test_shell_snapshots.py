import json
import pytest
from app.shell.formatter import ShellFormatter

def test_json_formatter(capsys):
    formatter = ShellFormatter(use_json=True)
    
    formatter.print_success("Operation completed", {"id": 123})
    captured = capsys.readouterr()
    
    output = json.loads(captured.out)
    assert output["status"] == "success"
    assert output["message"] == "Operation completed"
    assert output["data"]["id"] == 123

def test_json_formatter_table(capsys):
    formatter = ShellFormatter(use_json=True)
    
    formatter.print_table("Test Table", ["A", "B"], [[1, 2]])
    captured = capsys.readouterr()
    
    output = json.loads(captured.out)
    assert output["title"] == "Test Table"
    assert output["columns"] == ["A", "B"]
    assert output["rows"] == [[1, 2]]
