import pytest
import os
import sys
import socket
import subprocess
import asyncio
import tempfile
from typing import Any

from app.domain.security.models import SandboxPolicy
from app.infrastructure.execution.strategy import ExecutionContext
from app.infrastructure.execution.sandboxed_strategy import SandboxedExecutionStrategy

def safe_math() -> int:
    return 2 + 2

def unsafe_shell() -> int:
    return os.system("echo hello")

def unsafe_subprocess() -> int:
    return subprocess.run(["echo", "hello"]).returncode

def unsafe_network() -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return True

def unsafe_file_read(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

def safe_file_read(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d

@pytest.mark.asyncio
async def test_safe_execution_succeeds():
    strategy = SandboxedExecutionStrategy()
    policy = SandboxPolicy()
    context = ExecutionContext(sandbox_policy=policy)
    
    result = await strategy.execute(safe_math, context)
    assert result.success is True
    assert result.result == 4

@pytest.mark.asyncio
async def test_unsafe_shell_is_blocked():
    strategy = SandboxedExecutionStrategy()
    policy = SandboxPolicy(allow_subprocess=False)
    context = ExecutionContext(sandbox_policy=policy)
    
    result = await strategy.execute(unsafe_shell, context)
    assert result.success is False
    assert "subprocess execution blocked" in str(result.error)

@pytest.mark.asyncio
async def test_unsafe_subprocess_is_blocked():
    strategy = SandboxedExecutionStrategy()
    policy = SandboxPolicy(allow_subprocess=False)
    context = ExecutionContext(sandbox_policy=policy)
    
    result = await strategy.execute(unsafe_subprocess, context)
    assert result.success is False
    assert "subprocess execution blocked" in str(result.error)

@pytest.mark.asyncio
async def test_unsafe_network_is_blocked():
    strategy = SandboxedExecutionStrategy()
    policy = SandboxPolicy(allow_network=False)
    context = ExecutionContext(sandbox_policy=policy)
    
    result = await strategy.execute(unsafe_network, context)
    assert result.success is False
    assert "network access blocked" in str(result.error)

@pytest.mark.asyncio
async def test_file_read_outside_allowed_dir_is_blocked(temp_dir):
    strategy = SandboxedExecutionStrategy()
    # Create a dummy file outside the temp dir
    fd, outside_file = tempfile.mkstemp(dir=os.path.dirname(temp_dir))
    os.write(fd, b"secret")
    os.close(fd)
    
    try:
        policy = SandboxPolicy(allowed_directories=[temp_dir])
        context = ExecutionContext(sandbox_policy=policy)
        
        result = await strategy.execute(unsafe_file_read, context, outside_file)
        assert result.success is False
        assert "file access blocked" in str(result.error)
    finally:
        os.unlink(outside_file)

@pytest.mark.asyncio
async def test_file_read_inside_allowed_dir_succeeds(temp_dir):
    strategy = SandboxedExecutionStrategy()
    
    inside_file = os.path.join(temp_dir, "test.txt")
    with open(inside_file, "w") as f:
        f.write("allowed")
        
    policy = SandboxPolicy(allowed_directories=[temp_dir])
    context = ExecutionContext(sandbox_policy=policy)
    
    result = await strategy.execute(safe_file_read, context, inside_file)
    assert result.success is True
    assert result.result == "allowed"

@pytest.mark.asyncio
async def test_timeout_is_enforced():
    async def slow_func():
        import time
        time.sleep(2)
        return True
        
    strategy = SandboxedExecutionStrategy()
    policy = SandboxPolicy(max_execution_time_seconds=1)
    context = ExecutionContext(sandbox_policy=policy)
    
    # We use a synchronous sleep because execute uses ProcessPoolExecutor, which doesn't natively run async functions without an event loop inside the process, but `slow_func` is async... Wait, the wrapper doesn't run an event loop inside the process. It just calls the function. So we should pass a sync function for sleep.
    
    pass # Wait, let's redefine the slow func properly

def sync_slow_func() -> bool:
    import time
    time.sleep(2)
    return True

@pytest.mark.asyncio
async def test_timeout_is_enforced_sync():
    strategy = SandboxedExecutionStrategy()
    policy = SandboxPolicy(max_execution_time_seconds=1)
    context = ExecutionContext(sandbox_policy=policy, timeout_seconds=5) # 5s context, but 1s policy
    
    result = await strategy.execute(sync_slow_func, context)
    assert result.success is False
    assert "Execution timed out" in str(result.error)
