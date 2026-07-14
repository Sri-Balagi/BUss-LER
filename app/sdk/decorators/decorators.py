import functools
from typing import Any, Callable


def capability(name: str, description: str = ""):
    """
    Decorator to mark a Python function as a BizOS capability/tool.
    Can be discovered automatically by the BizOS ToolRegistry.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func.__is_bizos_capability__ = True
        func.__capability_name__ = name
        func.__capability_desc__ = description
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def shell_command(name: str):
    """
    Decorator to mark a function as an executable command within BizShell.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func.__is_bizos_shell_command__ = True
        func.__shell_command_name__ = name
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
