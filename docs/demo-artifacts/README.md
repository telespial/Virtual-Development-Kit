# Demo Artifacts

These artifacts are generated from the current Phase 4 validation flow.

- `golden-path-terminal.txt`: terminal output capture from EmbeddedX golden-path run
- `reports/*.json`: replay validation reports for all scenarios

Regenerate:

```bash
cd /home/user/python_projects/Virtual-Development-Kit
./scripts/run_phase4_validation_suite.sh
cp build/reports/*.json docs/demo-artifacts/reports/
```

Retention policy:
- [`../ARTIFACT_RETENTION_POLICY.md`](../ARTIFACT_RETENTION_POLICY.md)
