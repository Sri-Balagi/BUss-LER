import json
from pathlib import Path

class ReportingEngine:
    def __init__(self, reports_dir="tests/integration/validation_harness/reports", manifest_dir="tests/integration/validation_harness/manifests"):
        self.reports_dir = Path(reports_dir)
        self.manifest_dir = Path(manifest_dir)
        self.results = []
        
    def generate_report(self, scenario, trace, validator_results, coverage):
        report = {
            "scenario": scenario.scenario_id,
            "overall_pass": all(r[0] for r in validator_results.values()),
            "root_cause": "None" if all(r[0] for r in validator_results.values()) else "Cognitive Model Gap",
            "coverage": coverage,
            "validator_results": {k: {"passed": v[0], "message": v[1]} for k, v in validator_results.items()}
        }
        self.results.append(report)
        
        # Write JSON report
        report_path_json = self.reports_dir / f"{scenario.scenario_id}_report.json"
        with open(report_path_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        # Write Markdown report
        report_path_md = self.reports_dir / f"{scenario.scenario_id}_report.md"
        with open(report_path_md, "w", encoding="utf-8") as f:
            f.write(f"# Validation Report: {scenario.scenario_id}\n\n")
            f.write(f"**Overall Pass:** {'✅ PASSED' if report['overall_pass'] else '❌ FAILED'}\n\n")
            f.write(f"**Root Cause:** {report['root_cause']}\n\n")
            f.write(f"## Validator Results\n\n")
            for k, v in report['validator_results'].items():
                status = '✅' if v['passed'] else '❌'
                f.write(f"- **{k}**: {status} ({v['message']})\n")
        
    def generate_manifest(self, module_name):
        manifest = {
            "module": module_name,
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r["overall_pass"]),
            "failed": sum(1 for r in self.results if not r["overall_pass"])
        }
        with open(self.manifest_dir / f"{module_name}_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
