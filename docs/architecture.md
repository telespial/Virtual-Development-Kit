# VDK Architecture Notes

## Intent

VDK should give EmbeddedX a virtual execution target that is useful for engineering and demonstration work before full physical bring-up.

## Layering

### 1. Host Layer
Responsible for:
- windowing / UI
- framebuffer presentation
- debug overlays
- simulation controls
- replay or scripted input

### 2. Device Model Layer
Responsible for:
- device instances
- peripheral behaviors
- register-model surfaces
- MMIO responses
- virtual interrupt triggers

### 3. Board Composition Layer
Responsible for:
- assembling the virtual board from parts
- wiring virtual peripherals together
- assigning addresses / buses / interrupts
- mapping board identity and revision

### 4. MRD / MRC Integration Layer
Responsible for:
- consuming machine-readable hardware knowledge
- providing virtual target metadata
- constraining device and connectivity assumptions

### 5. Execution Adapter Layer
Responsible for:
- binding firmware or firmware-like logic to the virtual target
- abstracting what “runs” on the target in phase 1 vs later phases

## Suggested Phasing

### Phase 1
- architecture + repo layout
- one virtual board
- one display path
- one sensor path
- simple host loop or firmware adapter

### Phase 2
- richer MMIO / register behavior
- basic interrupt/event semantics
- more realistic timing surfaces
- MRD-assisted target generation

### Phase 3
- deeper firmware execution support
- replayable validation scenarios
- possible JIT/emulation backend exploration
