"""BizOS Doctor CLI — Command line diagnostic tool."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

# Load .env before running checks
load_dotenv()

from app.infrastructure.validation.doctor import BizOSDoctor

def main():
    print("=================================================================")
    print("                BizOS CORE PREFLIGHT DIAGNOSTICS                 ")
    print("=================================================================")
    
    doctor = BizOSDoctor()
    results = asyncio.run(doctor.run_diagnostics())
    
    for service, info in results["checks"].items():
        st = info.get("status", "UNKNOWN")
        msg = info.get("message", "")
        symbol = "[OK]  " if st == "OK" else ("[WARN]" if st == "WARN" else "[FAIL]")
        print(f" {symbol} {service.upper():<15}: {msg}")
        
    print("-----------------------------------------------------------------")
    summary = results["summary"]
    print(f" Status  : {results['status']}")
    print(f" Passed  : {summary['passed']}/{summary['total']}")
    print(f" Failed  : {summary['failed']}/{summary['total']}")
    print(f" Warnings: {summary['warnings']}/{summary['total']}")
    print("=================================================================")

if __name__ == "__main__":
    main()
