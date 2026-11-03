"""Record human approval of an observational model after scientific review."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approver", required=True)
    parser.add_argument("--evidence", required=True, help="Path or reference to the completed review evidence")
    parser.add_argument("--manifest", default="models/ndvi_forecast_rf.manifest.json")
    args = parser.parse_args()
    path = Path(args.manifest)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("dataset_kind") != "observational" or not manifest.get("observational_gate_passed"):
        raise SystemExit("Model cannot be approved: observational validation gate has not passed")
    manifest.update({
        "production_approved": True,
        "approved_by": args.approver,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "approval_evidence": args.evidence,
    })
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Approved {manifest['model_version']} by {args.approver}")


if __name__ == "__main__":
    main()
