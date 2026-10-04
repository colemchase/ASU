#!/usr/bin/env bash
# Run the required Locust scenarios and preserve raw framework reports.
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$project_dir"

timestamp="$(date +%Y%m%d-%H%M%S)"
results_root="locust_results/$timestamp"
mkdir -p "$results_root"

run_scenario() {
  local users="$1"
  local spawn_rate="$2"
  local run_seconds="$3"
  local scenario_dir="$results_root/users-${users}"
  mkdir -p "$scenario_dir/artifacts"

  echo "Running Locust: users=$users spawn_rate=$spawn_rate duration=${run_seconds}s"
  CSE565_PROFILE=standard \
  CSE565_API_MODE=simulated \
  CSE565_ARTIFACT_DIR="$scenario_dir/artifacts" \
  CSE565_DURATION_SECONDS="$run_seconds" \
  .venv/bin/locust -f locustfile.py --headless \
    --users "$users" --spawn-rate "$spawn_rate" --stop-timeout 15 \
    --csv "$scenario_dir/locust" --csv-full-history \
    --html "$scenario_dir/locust_report.html" \
    --only-summary \
    2>&1 | tee "$scenario_dir/locust_console.log"
}

# Immediate-spawn Task 3 tests: each requested user count is scheduled at once.
run_scenario 100 100 30
run_scenario 1000 1000 30
run_scenario 10000 10000 30

echo "Locust reports saved in: $results_root"
