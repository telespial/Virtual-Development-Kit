# Firmware Validation (Phase 3)

Phase 3 adds replayable validation so EmbeddedX teams can verify runtime behavior before hardware bring-up.

## What Phase 3 Adds

- Execution-adapter compatibility checks against the EmbeddedX exchange contract
- Replayable sensor scenarios with deterministic expected outcomes
- Machine-readable pass/fail report for pre-hardware signoff

## Validation Flow

1. Generate target + exchange artifacts (`vdk_phase2_integration.py`)
2. Run scenario replay validator (`vdk_phase3_validate.py`)
3. Inspect `vdk_validation_report.json`

## Example Command

```bash
cd /home/user/python_projects/Virtual-Development-Kit

python3 src/vdk_phase3_validate.py \
  --target-profile build/vdk_target_profile.json \
  --exchange-contract build/embeddedx_vdk_exchange.json \
  --scenario scenarios/example_sensor_monitor_baseline.json \
  --report-out build/vdk_validation_report.json
```

## Before-Hardware Story

This validation path demonstrates:
- signal contracts are complete for EIL advisory outputs
- runtime thresholds behave as expected on known traces
- teams can catch integration defects before flashing firmware
