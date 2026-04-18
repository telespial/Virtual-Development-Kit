#!/usr/bin/env python3
"""Phase 2 bridge: MRD/MRC/Intent/MDP/EIL -> VDK target + EmbeddedX exchange artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_scalar(value: str) -> Any:
    cleaned = value.strip().strip("'").strip('"')
    if cleaned.lower() == "true":
        return True
    if cleaned.lower() == "false":
        return False
    try:
        if "." in cleaned:
            return float(cleaned)
        return int(cleaned)
    except ValueError:
        return cleaned


def _parse_simple_intent_yaml(path: Path) -> dict[str, Any]:
    """Parse the constrained intent YAML used by EmbeddedX example projects."""
    text = path.read_text(encoding="utf-8")
    data: dict[str, Any] = {"inputs": [], "outputs": [], "runtime": {}}
    section: str | None = None
    current_item: dict[str, Any] | None = None
    runtime_subsection: str | None = None

    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        if line in {"inputs:", "outputs:", "runtime:"}:
            section = line[:-1]
            current_item = None
            runtime_subsection = None
            continue

        if section in {"inputs", "outputs"}:
            if line.startswith("- "):
                item: dict[str, Any] = {}
                payload = line[2:].strip()
                if ":" in payload:
                    key, value = payload.split(":", 1)
                    item[key.strip()] = _parse_scalar(value)
                data[section].append(item)
                current_item = item
                continue
            if current_item and ":" in line:
                key, value = line.split(":", 1)
                current_item[key.strip()] = _parse_scalar(value)
                continue

        if section == "runtime" and ":" in line:
            if line.endswith(":") and indent <= 2:
                runtime_subsection = line[:-1]
                data["runtime"].setdefault(runtime_subsection, {})
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            parsed = _parse_scalar(value)
            if indent >= 4 and runtime_subsection:
                subsection = data["runtime"].setdefault(runtime_subsection, {})
                if isinstance(subsection, dict):
                    subsection[key] = parsed
            else:
                data["runtime"][key] = parsed
                runtime_subsection = None

    return data


def _read_intent(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    suffix = path.suffix.lower()
    if suffix in {".json"}:
        return _read_json(path)
    if suffix in {".yaml", ".yml"}:
        return _parse_simple_intent_yaml(path)
    raise ValueError(f"Unsupported intent format: {path}")


def _collect_signals(
    intent: dict[str, Any], mdp: dict[str, Any], eil: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inputs: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []
    seen_inputs: set[str] = set()
    seen_outputs: set[str] = set()

    for entry in mdp.get("inputs", []):
        name = str(entry.get("name", "")).strip()
        if name and name not in seen_inputs:
            inputs.append(entry)
            seen_inputs.add(name)
    for entry in intent.get("inputs", []):
        name = str(entry.get("name", "")).strip()
        if name and name not in seen_inputs:
            inputs.append(entry)
            seen_inputs.add(name)

    for entry in mdp.get("outputs", []):
        name = str(entry.get("name", "")).strip()
        if name and name not in seen_outputs:
            outputs.append(entry)
            seen_outputs.add(name)
    for entry in intent.get("outputs", []):
        name = str(entry.get("name", "")).strip()
        if name and name not in seen_outputs:
            outputs.append(entry)
            seen_outputs.add(name)

    if eil.get("reason_codes") and "reason_code" not in seen_outputs:
        outputs.append({"name": "reason_code", "type": "string"})
        seen_outputs.add("reason_code")
    if "alert_state" not in seen_outputs:
        outputs.append({"name": "alert_state", "type": "enum"})
        seen_outputs.add("alert_state")
    if "anomaly_score" not in seen_outputs:
        outputs.append({"name": "anomaly_score", "type": "float"})
        seen_outputs.add("anomaly_score")

    return inputs, outputs


def _derive_runtime(
    mrd: dict[str, Any], intent: dict[str, Any], mdp: dict[str, Any], eil: dict[str, Any]
) -> dict[str, Any]:
    runtime = intent.get("runtime", {})
    thresholds = runtime.get("alert_thresholds", {})
    if not isinstance(thresholds, dict):
        thresholds = {}

    sample_hz = runtime.get("sample_hz")
    if sample_hz is None:
        sample_hz = mrd.get("constraints", {}).get("recommended_sample_hz")
    if sample_hz is None:
        first_input = (mdp.get("inputs") or [{}])[0]
        sample_hz = first_input.get("sampleRateHz", 10)

    mode = eil.get("runtime_mode") or runtime.get("mode") or "monitor"
    return {
        "mode": mode,
        "sample_hz": sample_hz,
        "alert_thresholds": {
            "temp_c_high": thresholds.get("temp_c_high", 65.0),
            "vibration_g_high": thresholds.get("vibration_g_high", 1.2),
        },
    }


def _build_target_profile(
    mrd: dict[str, Any],
    mrc: dict[str, Any],
    runtime: dict[str, Any],
    source_paths: dict[str, str | None],
) -> dict[str, Any]:
    mmio: list[dict[str, Any]] = []
    base_start = 0x40000000
    stride = 0x1000
    for idx, peripheral in enumerate(mrd.get("peripherals", [])):
        base = base_start + idx * stride
        mmio.append(
            {
                "name": peripheral.get("name", f"peripheral_{idx}"),
                "type": peripheral.get("type", "unknown"),
                "base_addr": f"0x{base:08X}",
                "span_bytes": stride,
            }
        )

    nets = mrc.get("nets", []) if isinstance(mrc, dict) else []
    signal_roles = sorted(
        {
            str(net.get("signal_role")).strip()
            for net in nets
            if isinstance(net, dict) and net.get("signal_role")
        }
    )
    board = mrc.get("board", {}) if isinstance(mrc, dict) else {}

    return {
        "schema": "embeddedx.vdk.target.v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "board": {
            "name": board.get("name") or mrd.get("part_number") or "virtual_target",
            "revision": board.get("revision", "virtual"),
            "vendor": mrd.get("vendor", "unknown"),
        },
        "cpu": mrd.get("core", {}),
        "memory": mrd.get("memory", {}),
        "peripherals_mmio": mmio,
        "connectivity_summary": {
            "net_count": len(nets),
            "signal_roles": signal_roles,
            "component_count": len(mrc.get("components", [])) if isinstance(mrc, dict) else 0,
        },
        "runtime": runtime,
        "source_inputs": source_paths,
    }


def _build_exchange_contract(
    target_profile_path: Path,
    exchange_path: Path,
    runtime_stub_path: Path,
    runtime: dict[str, Any],
    inputs: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
    eil: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "embeddedx.vdk.exchange.v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            "target_profile": str(target_profile_path),
            "exchange_contract": str(exchange_path),
            "runtime_stub": str(runtime_stub_path),
        },
        "io": {
            "inputs": inputs,
            "outputs": outputs,
        },
        "consumers": {
            "codemaster": {
                "target_profile_ref": str(target_profile_path),
                "input_signal_names": [str(item.get("name", "")) for item in inputs],
            },
            "eil": {
                "runtime_mode": runtime.get("mode"),
                "integration_api": eil.get("integration_api", "eil_infer()"),
                "reason_codes": eil.get("reason_codes", []),
            },
            "embeddedx": {
                "inject_ready": True,
                "notes": "Use this contract to wire generated app I/O to VDK target interfaces.",
            },
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_runtime_stub(path: Path, integration_api: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    func_name = integration_api.split("(")[0].strip() or "eil_infer"
    content = f"""#include <stddef.h>

/* Phase 2 runtime stub generated by VDK bridge.
 * Replace internals with model execution while preserving the interface boundary.
 */
int {func_name}(const float *inputs,
                unsigned int input_count,
                float *anomaly_score,
                int *alert_state,
                const char **reason_code)
{{
    (void)inputs;
    (void)input_count;
    if (anomaly_score) {{
        *anomaly_score = 0.0f;
    }}
    if (alert_state) {{
        *alert_state = 0;
    }}
    if (reason_code) {{
        *reason_code = "none";
    }}
    return 0;
}}
"""
    path.write_text(content, encoding="utf-8")


def _write_inject_manifest(
    path: Path, target_profile: Path, exchange_contract: Path, runtime_stub: Path
) -> None:
    manifest = {
        "schema": "embeddedx.inject.v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            "target_profile": str(target_profile),
            "exchange_contract": str(exchange_contract),
            "runtime_stub": str(runtime_stub),
        },
        "inject_steps": [
            "Load target profile in CodeMaster board adapter.",
            "Bind exchange inputs/outputs to generated app signals.",
            "Compile with VDK execution adapter before hardware flash.",
        ],
    }
    _write_json(path, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Phase 2 VDK integration artifacts for EmbeddedX."
    )
    parser.add_argument("--mrd", required=True, help="Path to MRD .msd/.json file")
    parser.add_argument("--mrc", help="Path to MRC .json file")
    parser.add_argument("--intent", help="Path to EmbeddedX intent (.yaml/.yml/.json)")
    parser.add_argument("--mdp", help="Path to MDP .json file")
    parser.add_argument("--eil", help="Path to EIL .json file")
    parser.add_argument(
        "--target-out",
        default="build/vdk_target_profile.json",
        help="Target profile output path",
    )
    parser.add_argument(
        "--exchange-out",
        default="build/embeddedx_vdk_exchange.json",
        help="Exchange contract output path",
    )
    parser.add_argument(
        "--runtime-stub-out",
        default="build/eil_runtime_stub.c",
        help="Generated EIL runtime stub output path",
    )
    parser.add_argument(
        "--inject-manifest-out",
        default="build/embeddedx_inject_manifest.json",
        help="EmbeddedX inject manifest output path",
    )
    args = parser.parse_args()

    mrd_path = Path(args.mrd).resolve()
    mrc_path = Path(args.mrc).resolve() if args.mrc else None
    intent_path = Path(args.intent).resolve() if args.intent else None
    mdp_path = Path(args.mdp).resolve() if args.mdp else None
    eil_path = Path(args.eil).resolve() if args.eil else None
    target_out = Path(args.target_out).resolve()
    exchange_out = Path(args.exchange_out).resolve()
    runtime_stub_out = Path(args.runtime_stub_out).resolve()
    inject_manifest_out = Path(args.inject_manifest_out).resolve()

    mrd = _read_json(mrd_path)
    mrc = _read_json(mrc_path) if mrc_path else {}
    intent = _read_intent(intent_path)
    mdp = _read_json(mdp_path) if mdp_path else {}
    eil = _read_json(eil_path) if eil_path else {}

    runtime = _derive_runtime(mrd, intent, mdp, eil)
    inputs, outputs = _collect_signals(intent, mdp, eil)
    source_paths = {
        "mrd": str(mrd_path),
        "mrc": str(mrc_path) if mrc_path else None,
        "intent": str(intent_path) if intent_path else None,
        "mdp": str(mdp_path) if mdp_path else None,
        "eil": str(eil_path) if eil_path else None,
    }

    target_profile = _build_target_profile(mrd, mrc, runtime, source_paths)
    _write_json(target_out, target_profile)

    exchange_contract = _build_exchange_contract(
        target_out,
        exchange_out,
        runtime_stub_out,
        runtime,
        inputs,
        outputs,
        eil,
    )
    _write_json(exchange_out, exchange_contract)

    _write_runtime_stub(runtime_stub_out, str(eil.get("integration_api", "eil_infer()")))
    _write_inject_manifest(inject_manifest_out, target_out, exchange_out, runtime_stub_out)

    print("Phase 2 artifacts generated:")
    print(f"- target profile: {target_out}")
    print(f"- exchange contract: {exchange_out}")
    print(f"- runtime stub: {runtime_stub_out}")
    print(f"- inject manifest: {inject_manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
