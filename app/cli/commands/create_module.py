import os
import shutil
import sys
from pathlib import Path
from app.reference_library.registry import get_provider

def run(args):
    module_name = args.name.lower().replace("-", "_").replace(" ", "_")
    template_dir = Path("app/templates/module")
    target_dir = Path(f"app/modules/{module_name}")
    
    if target_dir.exists() and not getattr(args, "force", False):
        print(f"Error: Module '{module_name}' already exists. Use --force to regenerate.")
        sys.exit(1)
        
    print(f"Scaffolding module '{module_name}'...")
    
    # Copy template
    if not target_dir.exists():
        shutil.copytree(template_dir, target_dir)
    
    # Replace template variables
    module_class_name = "".join([word.capitalize() for word in module_name.split("_")]) + "Module"
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace("{module_name}", module_name)
                content = content.replace("{module_class}", module_class_name)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                    
    if args.reference:
        print(f"Applying reference implementation for '{module_name}'...")
        provider = get_provider(module_name)
        if provider:
            km = provider.build()
            # Regenerate ai/cognition.py with the assembled knowledge model
            repr_km = repr(km).replace("datetime.datetime(", "datetime(")
            cognition_code = f"""# Generated from Reference Provider
from app.core.modules.ai.cognition import *
from datetime import datetime

{module_name.upper()}_KNOWLEDGE_MODEL = {repr_km}
"""
            with open(os.path.join(target_dir, "ai", "cognition.py"), "w", encoding="utf-8") as f:
                f.write(cognition_code)
                
            # Attempt to format with black if available
            try:
                import subprocess
                subprocess.run(["black", str(os.path.join(target_dir, "ai", "cognition.py"))], capture_output=True)
            except Exception:
                pass
        else:
            print(f"Warning: No reference provider found for '{module_name}'.")

    print(f"Successfully created module '{module_name}'.")
