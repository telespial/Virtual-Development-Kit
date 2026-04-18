#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-dry-run}"

TARGETS=(
  "${ROOT_DIR}/build/reports"
  "${ROOT_DIR}/docs/demo-artifacts/reports"
  "${ROOT_DIR}/docs/demo-artifacts/golden-path-terminal.txt"
)

echo "ARTIFACT_CLEANUP mode=${MODE}"
for target in "${TARGETS[@]}"; do
  if [[ -e "${target}" ]]; then
    echo "ARTIFACT_CLEANUP target=${target} action=remove"
    if [[ "${MODE}" == "apply" ]]; then
      rm -rf "${target}"
    fi
  else
    echo "ARTIFACT_CLEANUP target=${target} action=skip reason=missing"
  fi
done

if [[ "${MODE}" == "apply" ]]; then
  mkdir -p "${ROOT_DIR}/docs/demo-artifacts/reports"
  echo "ARTIFACT_CLEANUP status=complete"
else
  echo "ARTIFACT_CLEANUP status=dry-run-complete"
fi
