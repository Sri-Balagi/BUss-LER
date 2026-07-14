import os
import shutil
from pathlib import Path
from typing import Any, Dict

from app.sdk.manifest.app_manifest import AppManifest


class TemplateValidator:
    """Validates that a generated template is structurally sound."""
    
    @staticmethod
    def validate_app_template(path: str) -> bool:
        manifest_path = os.path.join(path, "manifest.json")
        if not os.path.exists(manifest_path):
            return False
            
        try:
            with open(manifest_path, "r") as f:
                import json
                data = json.load(f)
                AppManifest.model_validate(data)
            return True
        except Exception:
            return False


class Scaffolder:
    """Generates boilerplate for Apps and Plugins."""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
        
    def create_app(self, name: str, output_dir: str) -> bool:
        """Scaffolds a new App."""
        template_path = os.path.join(self.templates_dir, "app_template")
        target_path = os.path.join(output_dir, name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found at {template_path}")
            
        shutil.copytree(template_path, target_path)
        
        # Validate the generated structure
        if not TemplateValidator.validate_app_template(target_path):
            shutil.rmtree(target_path)
            raise ValueError("Generated template failed validation. Aborting.")
            
        return True
        
    def create_plugin(self, name: str, output_dir: str) -> bool:
        """Scaffolds a new Plugin."""
        template_path = os.path.join(self.templates_dir, "plugin_template")
        target_path = os.path.join(output_dir, name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found at {template_path}")
            
        shutil.copytree(template_path, target_path)
        return True
