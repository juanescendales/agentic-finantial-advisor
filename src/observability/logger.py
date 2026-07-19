import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_RUNS_DIR = Path("runs")
_run_id: str | None = None
_run_file: Path | None = None


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(levelname)s  %(name)s  %(message)s")


def start_run() -> str:
    global _run_id, _run_file
    _run_id = uuid.uuid4().hex[:12]
    _RUNS_DIR.mkdir(exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    _run_file = _RUNS_DIR / f"{ts}_{_run_id}.jsonl"
    return _run_id


def log_node_event(
    node_name: str,
    *,
    status: str,
    model: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    latency_ms: float | None = None,
    revision_count: int = 0,
) -> None:
    event: dict[str, Any] = {
        "run_id": _run_id,
        "node_name": node_name,
        "status": status,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "revision_count": revision_count,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    line = json.dumps(event)
    if _run_file is None:
        print(line)
        return
    with _run_file.open("a") as f:
        f.write(line + "\n")
