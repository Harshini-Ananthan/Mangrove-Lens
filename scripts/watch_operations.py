"""Read-only live operations console for Mangrove Lens demonstrations.

The observer never starts, stops, or controls monitoring. The API, scheduler and
agents continue to run when this process is not open.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
COLORS = {
    "api": "\033[96m",
    "scheduler": "\033[94m",
    "orchestrator": "\033[95m",
    "acquisition_agent": "\033[92m",
    "data_quality_agent": "\033[36m",
    "feature_agent": "\033[35m",
    "forecast_agent": "\033[93m",
    "risk_decision_agent": "\033[91m",
    "reporting_agent": "\033[34m",
    "alert_agent": "\033[33m",
    "retraining_agent": "\033[95m",
}


def api_request(url: str, api_key: str = ""):
    headers = {"X-API-Key": api_key} if api_key else {}
    return urllib.request.Request(url, headers=headers)


def request_json(url: str, api_key: str = ""):
    with urllib.request.urlopen(api_request(url, api_key), timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def compact_details(details: dict) -> str:
    if not details:
        return ""
    preferred = [
        "provider", "earth_engine_project", "query_executed_at", "duration_seconds",
        "optical_images", "sar_images", "co_images", "valid_pixel_fraction",
        "quality_status", "model_version", "expected_ndvi", "actual_ndvi",
        "residual", "uncertainty", "anomaly_score", "severity", "risk_score",
        "decision_id", "report_path", "report_generated", "data_mode", "reason",
    ]
    ordered = {key: details[key] for key in preferred if key in details}
    for key, value in details.items():
        if key not in ordered and len(ordered) < 8:
            ordered[key] = value
    return json.dumps(ordered, ensure_ascii=True, separators=(", ", ": "), default=str)


def show_event(event: dict, color_enabled: bool):
    color = COLORS.get(event.get("source"), "\033[37m") if color_enabled else ""
    reset = RESET if color_enabled else ""
    bold = BOLD if color_enabled else ""
    dim = DIM if color_enabled else ""
    timestamp = event.get("timestamp", "")
    try:
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%H:%M:%S.%f")[:-3]
    except ValueError:
        pass
    source = event.get("source", "system").upper().replace("_", " ")
    stage = event.get("stage", "event").replace("_", " ")
    level = event.get("level", "info")
    marker = "!" if level in {"warning", "error"} else ">"
    print(f"{dim}{timestamp}{reset} {color}{bold}{marker} {source:<24}{reset} {stage}")
    print(f"             {event.get('message', '')}")
    context = []
    if event.get("job_id"):
        context.append(f"job={event['job_id']}")
    if event.get("period_start"):
        context.append(f"period={event['period_start']}")
    details = compact_details(event.get("details") or {})
    if context:
        print(f"             {dim}{' | '.join(context)}{reset}")
    if details:
        print(f"             {color}{details}{reset}")
    print(flush=True)


def banner(base_url: str, dashboard_url: str, health: dict | None, readiness: dict | None, dashboard_online: bool, color_enabled: bool):
    teal = "\033[96m" if color_enabled else ""
    green = "\033[92m" if color_enabled else ""
    reset = RESET if color_enabled else ""
    bold = BOLD if color_enabled else ""
    print(f"{teal}{bold}")
    print("  +--------------------------------------------------------------+")
    print("  |              MANGROVE LENS LIVE OPERATIONS                  |")
    print("  |     Read-only evidence stream - autonomous system view      |")
    print("  +--------------------------------------------------------------+")
    print(reset, end="")
    print(f"  API       : {base_url}")
    print(f"  Dashboard : {dashboard_url} / online={dashboard_online}")
    if health:
        satellite = health.get("satellite", {})
        model = health.get("model", {})
        print(f"  Satellite : {green}{satellite.get('provider')} / ready={satellite.get('ready')}{reset}")
        print(f"  Model     : {model.get('version')} / ready={model.get('ready')}")
    if readiness:
        print(f"  Database  : ready={readiness.get('database', {}).get('ready')}")
    print("  Mode      : OBSERVE ONLY (agents run independently of this console)")
    print("  Evidence  : persisted operational events + live service stream")
    print("  Stop view : Ctrl+C\n")


def main():
    parser = argparse.ArgumentParser(description="Watch Mangrove Lens agents and services in real time")
    parser.add_argument("--api", default="http://localhost:8000/api/v1", help="Mangrove Lens API base URL")
    parser.add_argument("--dashboard", default="http://localhost:5173", help="Dashboard URL to include in service status")
    parser.add_argument(
        "--api-key", default=os.getenv("MANGROVE_LENS_API_KEY", ""),
        help="Operator API key; defaults to MANGROVE_LENS_API_KEY",
    )
    parser.add_argument("--history", type=int, default=20, help="Recent events to print before following live events")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    args = parser.parse_args()
    base_url = args.api.rstrip("/")
    color_enabled = not args.no_color and sys.stdout.isatty()
    if os.name == "nt" and color_enabled:
        os.system("")  # enable virtual terminal processing in current Windows consoles

    try:
        health = request_json(f"{base_url}/health", args.api_key)
        readiness = request_json(f"{base_url}/readiness", args.api_key)
    except Exception as exc:
        health = None
        readiness = None
        print(f"Waiting for Mangrove Lens API: {exc}")
    try:
        with urllib.request.urlopen(args.dashboard, timeout=5) as response:
            dashboard_online = response.status == 200
    except Exception:
        dashboard_online = False
    banner(base_url, args.dashboard, health, readiness, dashboard_online, color_enabled)

    cursor = 0
    if args.history > 0:
        try:
            events = request_json(
                f"{base_url}/operations/events?latest=true&limit={min(args.history, 500)}",
                args.api_key,
            )
            for event in events[-args.history:]:
                show_event(event, color_enabled)
                cursor = max(cursor, int(event["id"]))
        except Exception as exc:
            print(f"Unable to load event history yet: {exc}\n")

    retry_seconds = 1
    while True:
        stream_url = f"{base_url}/operations/events/stream?{urllib.parse.urlencode({'after_id': cursor})}"
        try:
            print(f"{DIM if color_enabled else ''}Following live activity...{RESET if color_enabled else ''}\n")
            with urllib.request.urlopen(api_request(stream_url, args.api_key), timeout=90) as response:
                retry_seconds = 1
                data_lines = []
                for raw_line in response:
                    line = raw_line.decode("utf-8").rstrip("\r\n")
                    if line.startswith("data:"):
                        data_lines.append(line[5:].strip())
                    elif not line and data_lines:
                        event = json.loads("\n".join(data_lines))
                        cursor = max(cursor, int(event["id"]))
                        show_event(event, color_enabled)
                        data_lines.clear()
        except KeyboardInterrupt:
            print("\nObserver stopped. Mangrove Lens services and agents continue running.")
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as exc:
            print(f"Stream interrupted ({exc}); reconnecting in {retry_seconds}s...")
            time.sleep(retry_seconds)
            retry_seconds = min(retry_seconds * 2, 10)


if __name__ == "__main__":
    main()
