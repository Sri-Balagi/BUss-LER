"""
Continuous Regression Test Suite for BizOS.
Executes on every significant code change.
Covers:
- Core unit & integration contracts
- Architectural immutability & execution mode propagation
- Safety & multi-tenant isolation
- Bella Vista operational crisis simulation
- Wave 14 platform maturity suite
"""
import sys
import asyncio
import subprocess

def run_regression_suite():
    print("========================================================================")
    print("  [BizOS CONTINUOUS REGRESSION TEST SUITE]")
    print("========================================================================\n")

    # 1. Execute Phased Certification Suites (Waves 15 - 24)
    print("--- [1/3] EXECUTING CERTIFICATION SUITES (WAVES 15 - 24) ---")
    cmd_cert = [sys.executable, "-m", "pytest", "tests/certification/", "-v"]
    res_cert = subprocess.run(cmd_cert, capture_output=True, text=True)
    if res_cert.returncode == 0:
        print("  [OK] All Certification Suites Passed (Waves 15 - 24)\n")
    else:
        print(f"  [FAIL] Certification Suite Failed:\n{res_cert.stdout}\n{res_cert.stderr}")
        return False

    # 2. Execute Wave 14 Platform Maturity Verification
    print("--- [2/3] EXECUTING WAVE 14 PLATFORM MATURITY SUITE ---")
    cmd_w14 = [sys.executable, "demo_wave14_maturity.py"]
    res_w14 = subprocess.run(cmd_w14, capture_output=True, text=True)
    if res_w14.returncode == 0:
        print("  [OK] Wave 14 Platform Maturity Suite Passed\n")
    else:
        print(f"  [FAIL] Wave 14 Suite Failed:\n{res_w14.stdout}\n{res_w14.stderr}")
        return False

    # 3. Execute Bella Vista Multi-Agent Simulation
    print("--- [3/3] EXECUTING BELLA VISTA OPERATIONAL SIMULATION ---")
    cmd_bv = [sys.executable, "demo_bella_vista.py"]
    res_bv = subprocess.run(cmd_bv, capture_output=True, text=True)
    if res_bv.returncode == 0:
        print("  [OK] Bella Vista Multi-Agent Simulation Passed\n")
    else:
        print(f"  [FAIL] Bella Vista Simulation Failed:\n{res_bv.stdout}\n{res_bv.stderr}")
        return False

    print("========================================================================")
    print("  SUCCESS: CONTINUOUS REGRESSION SUITE PASSED 100% (0 REGRESSIONS)")
    print("========================================================================\n")
    return True

if __name__ == "__main__":
    success = run_regression_suite()
    if not success:
        sys.exit(1)
