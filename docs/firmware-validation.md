# Firmware Validation (Phase 3)

Phase 3 adds replayable validation so EmbeddedX teams can verify runtime behavior before hardware bring-up.

## What Phase 3 Adds

- Execution-adapter compatibility checks against the EmbeddedX exchange contract
- Replayable sensor scenarios with deterministic expected outcomes
- Machine-readable pass/fail report for pre-hardware signoff

## Validation Flow

1. Generate target + exchange artifacts (`vdk_phase2_integration.py`)
2. Run scenario replay validator (`vdk_phase3_validate.py`)
3. Inspect `build/reports/*.report.json`

## Example Command (Single Scenario)

```bash
cd /home/user/python_projects/Virtual-Development-Kit

python3 src/vdk_phase3_validate.py \
  --target-profile build/vdk_target_profile.json \
  --exchange-contract build/embeddedx_vdk_exchange.json \
  --scenario scenarios/example_sensor_monitor_baseline.json \
  --report-out build/reports/example_sensor_monitor_baseline.report.json
```

## Phase 4 Suite

Run all validation scenarios:

```bash
./scripts/run_phase4_validation_suite.sh
```

Default scenarios:
- `example_sensor_monitor_baseline.json`
- `example_sensor_monitor_noise_burst.json`
- `example_sensor_monitor_sensor_dropout.json`
- `example_sensor_monitor_threshold_edges.json`

## Before-Hardware Story

This validation path demonstrates:
- signal contracts are complete for EIL advisory outputs
- runtime thresholds behave as expected on known traces
- teams can catch integration defects before flashing firmware
