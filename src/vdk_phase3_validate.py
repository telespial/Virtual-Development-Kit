#!/usr/bin/env python3
"""Phase 3 firmware-style validation using replayable scenarios."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _compute_runtime_outputs(
    temp_c: float, vibration_g: float, temp_high: float, vibration_high: float
) -> dict[str, Any]:
    temp_ratio = max((temp_c - temp_high) / max(temp_high, 1.0), 0.0)
    vibe_ratio = max((vibration_g - vibration_high) / max(vibration_high, 1.0), 0.0)
    anomaly_score = max(temp_ratio, vibe_ratio)
    alert_state = 1 if anomaly_score > 0.0 else 0

    if temp_c >= temp_high and vibration_g >= vibration_high:
        reason_code = "temperature_and_vibration_high"
    elif temp_c >= temp_high:
        reason_code = "temperature_high"
    elif vibration_g >= vibration_high:
        reason_code = "vibration_high"
    else:
        reason_code = "none"

    return {
        "alert_state": alert_state,
        "anomaly_score": round(anomaly_score, 6),
        "reason_code": reason_code,
    }


def _evaluate_step(
    idx: int,
    step: dict[str, Any],
    temp_high: float,
    vibration_high: float,
) -> dict[str, Any]:
    temp_c = float(step.get("temp_c", 0.0))
    vibration_g = float(step.get("vibration_g", 0.0))
    observed = _compute_runtime_outputs(temp_c, vibration_g, temp_high, vibration_high)
    expected = step.get("expected", {})

    mismatches: list[str] = []
    if "alert_state" in expected and int(expected["alert_state"]) != int(observed["alert_state"]):
        mismatches.append(
            f"alert_state expected {expected['alert_state']} observed {observed['alert_state']}"
        )
    if "reason_code" in expected and str(expected["reason_code"]) != str(observed["reason_code"]):
        mismatches.append(
            f"reason_code expected {expected['reason_code']} observed {observed['reason_code']}"
        )
    if "anomaly_score_min" in expected and float(observed["anomaly_score"]) < float(
        expected["anomaly_score_min"]
    ):
        mismatches.append(
            "anomaly_score below minimum "
            f"{expected['anomaly_score_min']} observed {observed['anomaly_score']}"
        )

    return {
        "index": idx,
        "input": {"temp_c": temp_c, "vibration_g": vibration_g},
        "expected": expected,
        "observed": observed,
        "pass": len(mismatches) == 0,
        "mismatches": mismatches,
    }


def _adapter_checks(exchange: dict[str, Any]) -> dict[str, Any]:
    inputs = exchange.get("io", {}).get("inputs", [])
    outputs = exchange.get("io", {}).get("outputs", [])
    output_names = {str(item.get("name", "")).strip() for item in outputs}
    required_outputs = {"alert_state", "anomaly_score", "reason_code"}
    missing_outputs = sorted(required_outputs - output_names)
    has_runtime_mode = bool(exchange.get("consumers", {}).get("eil", {}).get("runtime_mode"))

    return {
        "input_count": len(inputs),
        "output_count": len(outputs),
        "required_outputs": sorted(required_outputs),
        "missing_outputs": missing_outputs,
        "has_runtime_mode": has_runtime_mode,
        "compatible": len(missing_outputs) == 0 and has_runtime_mode,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 3 replayable validation scenario.")
    parser.add_argument("--target-profile", required=True, help="Path to vdk_target_profile.json")
    parser.add_argument(
        "--exchange-contract", required=True, help="Path to embeddedx_vdk_exchange.json"
    )
    parser.add_argument("--scenario", required=True, help="Path to replay scenario JSON")
    parser.add_argument("--report-out", default="build/vdk_validation_report.json")
    args = parser.parse_args()

    target_profile = _read_json(Path(args.target_profile).resolve())
    exchange = _read_json(Path(args.exchange_contract).resolve())
    scenario = _read_json(Path(args.scenario).resolve())

    runtime = target_profile.get("runtime", {})
    thresholds = runtime.get("alert_thresholds", {})
    temp_high = float(thresholds.get("temp_c_high", 65.0))
    vibration_high = float(thresholds.get("vibration_g_high", 1.2))

    steps = scenario.get("steps", [])
    results = [
        _evaluate_step(idx, step, temp_high=temp_high, vibration_high=vibration_high)
        for idx, step in enumerate(steps)
    ]
    pass_count = sum(1 for item in results if item["pass"])
    fail_count = len(results) - pass_count

    adapter = _adapter_checks(exchange)
    overall_pass = fail_count == 0 and adapter["compatible"]

    report = {
        "schema": "embeddedx.vdk.validation.v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": {
            "name": scenario.get("name", "unnamed"),
            "description": scenario.get("description", ""),
            "step_count": len(steps),
        },
        "runtime_thresholds": {
            "temp_c_high": temp_high,
            "vibration_g_high": vibration_high,
        },
        "adapter_checks": adapter,
        "results": results,
        "summary": {
            "overall_pass": overall_pass,
            "step_pass_count": pass_count,
            "step_fail_count": fail_count,
        },
        "before_hardware_story": (
            "This report confirms signal contract compatibility and expected EIL advisory behavior "
            "on replayed sensor traces before flashing physical hardware."
        ),
    }

    report_out = Path(args.report_out).resolve()
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Validation report written: {report_out}")
    print(
        "Summary: "
        f"overall_pass={overall_pass} "
        f"steps_passed={pass_count} steps_failed={fail_count} "
        f"adapter_compatible={adapter['compatible']}"
    )
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
