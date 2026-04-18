# Artifact Retention Policy

This policy defines what validation/demo artifacts are committed versus generated in CI.

## Commit Policy

Commit these to the repository:
- `docs/demo-artifacts/golden-path-terminal.txt` (latest representative run)
- `docs/demo-artifacts/reports/*.json` (latest representative scenario reports)

Do not commit these:
- `build/` runtime artifacts from local runs except where explicitly documented
- transient CI working files

## Refresh Cadence

- Refresh demo artifacts at least once per milestone phase.
- Refresh immediately when validation logic or scenario semantics change.

## Naming

- Scenario reports: `<scenario_name>.report.json`
- Golden path terminal capture: `golden-path-terminal.txt`

## Cleanup

Dry run:
```bash
./tools/cleanup_artifacts.sh
```

Apply cleanup:
```bash
./tools/cleanup_artifacts.sh apply
```
