#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
FIXTURE_DIR="${ROOT_DIR}/fixtures/example_sensor_monitor"
SCENARIO_DIR="${ROOT_DIR}/scenarios"
REPORT_DIR="${BUILD_DIR}/reports"

mkdir -p "${BUILD_DIR}" "${REPORT_DIR}"

python3 "${ROOT_DIR}/src/vdk_phase2_integration.py" \
  --mrd "${FIXTURE_DIR}/mrd/EXAMPLE_SENSOR_NODE.msd" \
  --mrc "${FIXTURE_DIR}/mrc/EXAMPLE_SENSOR_NODE.mrc.json" \
  --intent "${FIXTURE_DIR}/intent/system_intent.yaml" \
  --mdp "${FIXTURE_DIR}/model/example_sensor_monitor.mdp.json" \
  --eil "${FIXTURE_DIR}/eil/example_sensor_monitor.eil.json" \
  --target-out "${BUILD_DIR}/vdk_target_profile.json" \
  --exchange-out "${BUILD_DIR}/embeddedx_vdk_exchange.json" \
  --runtime-stub-out "${BUILD_DIR}/eil_runtime_stub.c" \
  --inject-manifest-out "${BUILD_DIR}/embeddedx_inject_manifest.json"
echo "PHASE_SUMMARY phase=phase2 status=pass report_dir=${REPORT_DIR}"

for scenario in "${SCENARIO_DIR}"/example_sensor_monitor_*.json; do
  name="$(basename "${scenario}" .json)"
  report="${REPORT_DIR}/${name}.report.json"
  echo "PHASE_STEP phase=phase3 scenario=${name} status=running"
  python3 "${ROOT_DIR}/src/vdk_phase3_validate.py" \
    --target-profile "${BUILD_DIR}/vdk_target_profile.json" \
    --exchange-contract "${BUILD_DIR}/embeddedx_vdk_exchange.json" \
    --scenario "${scenario}" \
    --report-out "${report}"
  echo "PHASE_STEP phase=phase3 scenario=${name} status=pass report=${report}"
done

python3 "${ROOT_DIR}/src/vdk_minimal_demo.py" \
  --steps 3 \
  --target-profile "${BUILD_DIR}/vdk_target_profile.json" \
  --exchange-contract "${BUILD_DIR}/embeddedx_vdk_exchange.json"
echo "PHASE_SUMMARY phase=phase4 status=pass reports=${REPORT_DIR}"
