import logging
from typing import Dict, Any
import time

class MetricsRegistry:
    def __init__(self):
        self.counters = {}
        self.histograms = {}

    def inc(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        key = self._format_key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value

    def observe(self, name: str, value: float, labels: Dict[str, str] = None):
        key = self._format_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)

    def _format_key(self, name: str, labels: Dict[str, str]) -> str:
        if not labels:
            return name
        lbls = ",".join([f'{k}="{v}"' for k, v in sorted(labels.items())])
        return f"{name}{{{lbls}}}"
        
    def export_prometheus(self) -> str:
        lines = []
        for k, v in self.counters.items():
            lines.append(f"{k} {v}")
        return "\n".join(lines)

class TraceContext:
    def __init__(self, trace_id: str, span_id: str):
        self.trace_id = trace_id
        self.span_id = span_id
        self.start_time = time.time()

class Tracer:
    def start_span(self, name: str, trace_id: str = None) -> TraceContext:
        import uuid
        tid = trace_id or str(uuid.uuid4())
        sid = str(uuid.uuid4())
        logging.info(f"SPAN_START: name={name} trace_id={tid} span_id={sid}")
        return TraceContext(tid, sid)
        
    def end_span(self, ctx: TraceContext):
        duration = time.time() - ctx.start_time
        logging.info(f"SPAN_END: trace_id={ctx.trace_id} span_id={ctx.span_id} duration={duration}")
