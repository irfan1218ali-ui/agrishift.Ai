"""Copy the supplied Meteomatics saved response without its account identifier."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "api-samples" / "meteomatics" / "json.json"
OUTPUT = ROOT / "data" / "api-samples" / "meteomatics" / "demo_sample.example.json"


def build(source: Path = SOURCE, output: Path = OUTPUT) -> Path:
    payload = json.loads(Path(source).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("Expected a Meteomatics JSON response with a data list")
    payload.pop("user", None)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(build())
