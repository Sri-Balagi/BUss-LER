"""BizOS Initialization & Bootstrap Wizard — bizos init"""

import os
import sys
import shutil
from typing import Dict, Any


def run(args=None):
    print("\n========================================================================")
    print("  [BizOS Enterprise Platform — Bootstrap & Project Initializer]")
    print("========================================================================\n")

    cwd = os.getcwd()
    env_file = os.path.join(cwd, ".env")
    env_example = os.path.join(cwd, ".env.example")

    # 1. Environment File Bootstrap
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            shutil.copyfile(env_example, env_file)
            print("  [OK] Created .env configuration file from template (.env.example)")
        else:
            print("  [WARN] .env.example not found; creating minimal .env file...")
            with open(env_file, "w") as f:
                f.write("# BizOS Configuration\nAPP_ENV=development\nLOG_LEVEL=INFO\n")
            print("  [OK] Created default .env configuration file")
    else:
        print("  [OK] Existing .env file detected")

    # 2. Directory Structure Verification
    dirs_to_ensure = [
        "app/modules",
        "app/plugins",
        "app/connectors",
        "configs",
        "logs",
        "storage/memories",
    ]

    for d in dirs_to_ensure:
        full_path = os.path.join(cwd, d)
        os.makedirs(full_path, exist_ok=True)
        print(f"  [OK] Directory verified: {d}")

    # 3. Default Configuration & Key Checks
    has_gemini = False
    with open(env_file, "r") as f:
        content = f.read()
        if "GEMINI_API_KEY=" in content and not content.endswith("GEMINI_API_KEY=\n"):
            has_gemini = True

    print("\n------------------------------------------------------------------------")
    print("  [SUMMARY] Initialization completed successfully.")
    if not has_gemini:
        print("  [ACTION REQUIRED] Please edit .env and set your GEMINI_API_KEY before running bizos start.")
    else:
        print("  [NEXT STEP] Run 'bizos doctor' to verify system readiness or 'bizos start' to launch.")
    print("========================================================================\n")
