"""Digital Twin Drift Detector & Precision Metric Engine."""

from typing import Any, Dict
from app.domain.twin.models import DigitalTwinState


class DigitalTwinDriftDetector:
    """Calculates synchronization drift between real-world ground truth and Digital Twin properties."""

    @staticmethod
    def calculate_drift(real_world_state: Dict[str, Any], twin_state: DigitalTwinState) -> Dict[str, Any]:
        twin_props = twin_state.properties
        total_keys = set(real_world_state.keys()).union(set(twin_props.keys()))

        mismatched_keys = []
        for key in total_keys:
            real_val = real_world_state.get(key)
            twin_val = twin_props.get(key)
            if real_val != twin_val:
                mismatched_keys.append({"key": key, "real_val": real_val, "twin_val": twin_val})

        drift_count = len(mismatched_keys)
        total_count = max(1, len(total_keys))
        drift_pct = (drift_count / total_count) * 100.0
        sync_precision_pct = 100.0 - drift_pct

        return {
            "total_properties": len(total_keys),
            "mismatched_count": drift_count,
            "drift_percentage": round(drift_pct, 2),
            "sync_precision_pct": round(sync_precision_pct, 2),
            "mismatches": mismatched_keys,
            "is_in_sync": drift_count == 0,
        }
