# EmbeddedX Integration (Phase 2)

This phase connects spec artifacts to a runnable virtual target.

## Inputs

The VDK bridge accepts:
- MRD (`.msd` / JSON): hardware capabilities
- MRC (`.json`): board wiring and nets
- Intent (`.yaml` / `.json`): runtime goals and thresholds
- MDP (`.json`): model inputs/outputs
- EIL (`.json`): runtime mode and API boundary

## Generated Artifacts

`src/vdk_phase2_integration.py` produces:
- `vdk_target_profile.json`
- `embeddedx_vdk_exchange.json`
- `eil_runtime_stub.c`
- `embeddedx_inject_manifest.json`

These outputs provide:
- MDP to runtime input/output mapping
- EIL runtime stub boundary for integration
- EmbeddedX injection metadata for CodeMaster/EIL handoff

## Run with EmbeddedX Example Project

```bash
cd /home/user/python_projects/Virtual-Development-Kit

python3 src/vdk_phase2_integration.py \
  --mrd /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/mrd/EXAMPLE_SENSOR_NODE.msd \
  --mrc /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/mrc/EXAMPLE_SENSOR_NODE.mrc.json \
  --intent /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/intent/system_intent.yaml \
  --mdp /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/model/example_sensor_monitor.mdp.json \
  --eil /home/user/python_projects/EmbeddedX/projects/example_sensor_monitor/eil/example_sensor_monitor.eil.json
```

Then run the demo using the generated contract:

```bash
python3 src/vdk_minimal_demo.py \
  --steps 120 \
  --target-profile build/vdk_target_profile.json \
  --exchange-contract build/embeddedx_vdk_exchange.json
```

## Scope

Phase 2 is a contract bridge, not full emulation. It gives EmbeddedX a repeatable virtual target handoff before hardware bring-up.
