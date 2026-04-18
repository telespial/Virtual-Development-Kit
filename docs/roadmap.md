# VDK Roadmap

## Phase 0 - Repo Foundation
- create README
- create LICENSE.md
- create docs/
- create minimal source layout
- define scope boundaries

## Phase 1 - Demonstrable Virtual Target
- define address map abstraction
- define peripheral trait/interface
- implement one framebuffer display device
- implement one scripted sensor source
- implement one example virtual board
- create host-side demo

## Phase 2 - EmbeddedX Integration
- define how MRD/MRC inform virtual target creation
- define data exchange with EmbeddedX
- define how CodeMaster/EIL can consume the target

Current implementation:
- `src/vdk_phase2_integration.py` builds target, exchange, and injection artifacts
- generated `eil_runtime_stub.c` provides a fixed runtime boundary for early integration
- `vdk_minimal_demo.py` consumes generated runtime profile and IO contract

## Phase 3 - Firmware Validation
- support stronger execution adapter flows
- support replayable scenarios
- create a “before hardware” validation story

Current implementation:
- `src/vdk_phase3_validate.py` validates exchange adapter compatibility and advisory outputs
- `scenarios/example_sensor_monitor_baseline.json` provides deterministic replay input
- `docs/firmware-validation.md` documents before-hardware signoff flow

## Phase 4 - Release Readiness
- enforce validation in CI
- expand replay coverage
- define a repeatable alpha release gate

Current implementation:
- `.github/workflows/phase4-validation.yml` runs compile + suite checks on push and PR
- `scripts/run_phase4_validation_suite.sh` executes fixture-driven integration + scenario replay
- scenario set now includes baseline, noise burst, sensor dropout, and threshold edges

## Phase 6 - Reliability Hardening
- improve replay realism with timing and delayed-signal behavior
- enforce scenario source-of-truth consistency across repos
- standardize script summaries for CI parsing
- document retention and cleanup policy for demo/validation artifacts

Current implementation:
- validator supports deterministic jitter (`--seed`) and delayed replay (`delay_steps`, `delay_ms`)
- VDK CI now checks EmbeddedX scenario mirror consistency
- script outputs include `PHASE_SUMMARY` / `VALIDATION_SUMMARY` records
- retention policy and cleanup helper are documented in `docs/ARTIFACT_RETENTION_POLICY.md`

## Not Required for Phase 1
- full ARM accuracy
- perfect timing fidelity
- complete peripheral coverage
- full SoC emulation
