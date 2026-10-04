#!/usr/bin/env bash
# Task 5: sustained immediate-load test with a response-time SLO.
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$project_dir"

timestamp="$(date +%Y%m%d-%H%M%S)"
scenario_dir="locust_results/$timestamp/stress-users-10000"
mkdir -p "$scenario_dir/artifacts"

CSE565_PROFILE=standard \
CSE565_API_MODE=simulated \
CSE565_ARTIFACT_DIR="$scenario_dir/artifacts" \
CSE565_DURATION_SECONDS=300 \
CSE565_SLO_MS=500 \
.venv/bin/locust -f locustfile.py --headless \
  --users 10000 --spawn-rate 10000 --stop-timeout 30 \
  --csv "$scenario_dir/locust" --csv-full-history \
  --html "$scenario_dir/locust_report.html" \
  --only-summary \
  2>&1 | tee "$scenario_dir/locust_console.log"

echo "Locust Task 5 reports saved in: $scenario_dir"
