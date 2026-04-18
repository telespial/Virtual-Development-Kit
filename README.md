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

See [LICENSE.md](./LICENSE.md).
