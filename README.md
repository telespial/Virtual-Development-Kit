# Virtual Development Kit (VDK)

Virtual Development Kit (VDK) is the software-defined target layer for EmbeddedX.

It is intended to let engineers and automated tooling stand up a virtual embedded target before, during, or alongside physical hardware development. VDK should model enough of a board, device, or subsystem that firmware workflows, display workflows, sensor workflows, and integration logic can be exercised in a controlled environment.

## Relationship to EmbeddedX

EmbeddedX is the broader platform. VDK is one module in that platform.

- **EmbeddedX**: overall workflow and orchestration
- **MRD Studio / MRD specs**: machine-readable hardware capability and constraint modeling
- **MRC specs**: connectivity and board wiring knowledge
- **CodeMaster**: firmware synthesis / constrained generation engine
- **EIL**: embedded intelligence runtime layer
- **VDK**: virtual target execution, simulation, and validation environment

## Scope

Phase 1 should stay narrow and demonstrable.

VDK does **not** need to start as a cycle-accurate emulator or a full QEMU competitor.

The first useful goal is:

- a software-defined virtual board target
- a structured memory / MMIO model
- one or more virtual peripherals
- a host-facing display or framebuffer surface
- scripted or replayed sensor input
- enough execution plumbing to exercise firmware logic

## Recommended First Milestone

A good first milestone is:

1. define repository structure
2. define host/device boundary
3. define basic address map / MMIO abstraction
4. create one virtual display path
5. create one virtual sensor input path
6. create a minimal board demo that proves event flow

Examples of acceptable phase-1 demos:

- virtual LCD + button input + fake accelerometer feed
- virtual framebuffer + scripted telemetry overlay
- firmware-like event loop driving a virtual target board
- “bring-up before hardware arrives” demo showing display and sensor responses

## Phase 1 Runnable Demo
Run the minimum no-hardware demo:

```bash
cd /home/user/python_projects/Virtual-Development-Kit
python3 src/vdk_minimal_demo.py --steps 120 --fps 12
```

What it does:
- virtual framebuffer output (terminal-hosted LCD)
- fake sensor input stream (`temp_c`, `vibration_g`)
- simple deterministic update loop with alert state

## Phase 2 EmbeddedX Bridge
Generate integration artifacts from EmbeddedX project inputs:

```bash
cd /home/user/python_projects/Virtual-Development-Kit
python3 src/vdk_phase2_integration.py \
  --mrd /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/mrd/EXAMPLE_SENSOR_NODE.msd \
  --mrc /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/mrc/EXAMPLE_SENSOR_NODE.mrc.json \
  --intent /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/intent/system_intent.yaml \
  --mdp /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/model/example_sensor_monitor.mdp.json \
  --eil /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/eil/example_sensor_monitor.eil.json
```

Then run the demo with generated runtime thresholds and signal contract:

```bash
python3 src/vdk_minimal_demo.py \
  --steps 120 \
  --target-profile build/vdk_target_profile.json \
  --exchange-contract build/embeddedx_vdk_exchange.json
```

## Phase 3 Firmware Validation
Run replayable before-hardware validation:

```bash
python3 src/vdk_phase3_validate.py \
  --target-profile build/vdk_target_profile.json \
  --exchange-contract build/embeddedx_vdk_exchange.json \
  --scenario scenarios/example_sensor_monitor_baseline.json \
  --report-out build/reports/example_sensor_monitor_baseline.report.json
```

This produces a machine-readable pass/fail report with:
- execution-adapter compatibility checks
- expected vs observed EIL advisory outputs
- a pre-hardware validation summary

## Phase 4 CI + Scenario Suite
Run the complete suite locally:

```bash
./scripts/run_phase4_validation_suite.sh
```

This executes:
- Phase 2 artifact generation from local fixture inputs
- all replay scenarios in `scenarios/`
- short live demo smoke run

## Recommended Repo Layout

```text
Virtual-Development-Kit/
  README.md
  LICENSE.md
  docs/
    architecture.md
    roadmap.md
    first-demo.md
    embeddedx-integration.md
    firmware-validation.md
  src/
    vdk_minimal_demo.py
    vdk_phase2_integration.py
    vdk_phase3_validate.py
  scenarios/
    example_sensor_monitor_baseline.json
    example_sensor_monitor_noise_burst.json
    example_sensor_monitor_sensor_dropout.json
    example_sensor_monitor_threshold_edges.json
  scripts/
    run_phase4_validation_suite.sh
  fixtures/
    example_sensor_monitor/
  crates/
    vdk-core/
    vdk-devices/
    vdk-host/
    vdk-mrd/
```

## Guardrails

Do not let VDK become an uncontrolled “simulate everything” project on day one.

The priority is to establish a strong architecture and a compelling first demonstration, not perfect hardware fidelity.

## License

See [LICENSE.md](./LICENSE.md)
