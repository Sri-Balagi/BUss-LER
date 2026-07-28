import os
from pathlib import Path

def run(args):
    modules_dir = Path("app/modules")
    print("Installed BizOS Modules:")
    if not modules_dir.exists():
        print("No modules directory found.")
        return
        
    for item in modules_dir.iterdir():
        if item.is_dir() and (item / "module.py").exists():
            print(f" - {item.name}")
