#!/usr/bin/env python3
"""Scalable, reproducible load benchmark for the CSE 565 performance project.

This is intentionally separate from ``load_test_tasks.py``, which is the
instructor-provided starter.  A run represents a requested number of logical
users, while ``--max-workers`` limits active threads so 10,000 logical users
does not create 10,000 operating-system threads.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import shutil
import statistics
import tempfile
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


PROFILES = {
    # Profile used for a quick validation of the runner itself.
    "quick": {"dataset_size": 500, "db_delay": 0.002, "api_delay": 0.003,
              "file_bytes": 1_024, "compute_limit": 500},
    # Default: controlled enough to run on a student computer at 10,000 users.
    "standard": {"dataset_size": 5_000, "db_delay": 0.010, "api_delay": 0.015,
                 "file_bytes": 4_096, "compute_limit": 2_000},
    # An approximate copy of the starter workload. Use only for small runs.
    "teacher-equivalent": {"dataset_size": 100_000, "db_delay": 0.5, "api_delay": 0.0,
                           "file_bytes": 250_000, "compute_limit": 10_000},
}
TASK_NAMES = ("data_processing", "database_query", "api_request", "file_io", "computation", "logging")


@dataclass(frozen=True)
class RunConfig:
    users: int
    max_workers: int
    profile: str
    api_mode: str
    api_url: str
    request_timeout: float
    output_dir: Path


@dataclass
class UserResult:
    user_id: int
    durations_ms: dict[str, float]
    failures: list[str]


def elapsed_ms(operation: Callable[[], object]) -> tuple[float, object]:
    start = time.perf_counter()
    value = operation()
    return (time.perf_counter() - start) * 1_000, value


def percentile(values: list[float], percent: float) -> float:
    """Linearly interpolated percentile without an additional dependency."""
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def run_user(user_id: int, config: RunConfig, run_directory: Path, log_lock: threading.Lock) -> UserResult:
    profile = PROFILES[config.profile]
    rng = random.Random(user_id)
    durations: dict[str, float] = {}
    failures: list[str] = []

    def data_processing() -> int:
        return len(sorted(rng.randint(1, 1_000_000) for _ in range(profile["dataset_size"])))

    def database_query() -> str:
        time.sleep(profile["db_delay"])
        return "Query Complete"

    def api_request() -> int:
        if config.api_mode == "simulated":
            # A controlled response is the default: do not unintentionally send
            # 11,100 requests to a public service when running all three levels.
            time.sleep(profile["api_delay"])
            return 200
        request = urllib.request.Request(config.api_url, headers={"User-Agent": "CSE565-performance-benchmark/1.0"})
        with urllib.request.urlopen(request, timeout=config.request_timeout) as response:
            return response.status

    def file_io() -> int:
        # Per-user files prevent the data race in the starter's shared test_file.txt.
        payload = ("Load testing simulation. " * ((profile["file_bytes"] // 25) + 1)).encode()[:profile["file_bytes"]]
        path = run_directory / "temporary" / f"user-{user_id}.txt"
        path.write_bytes(payload)
        size = len(path.read_bytes())
        path.unlink(missing_ok=True)
        return size

    def computation() -> int:
        return sum(value * value for value in range(profile["compute_limit"]))

    def logging_task() -> str:
        # A lock makes the shared log deterministic and prevents interleaved records.
        with log_lock:
            with (run_directory / "execution.log").open("a", encoding="utf-8") as handle:
                handle.write(f"user={user_id}, timestamp={datetime.now(timezone.utc).isoformat()}\n")
        return "Log Written"

    operations: tuple[tuple[str, Callable[[], object]], ...] = (
        ("data_processing", data_processing),
        ("database_query", database_query),
        ("api_request", api_request),
        ("file_io", file_io),
        ("computation", computation),
        ("logging", logging_task),
    )
    for name, operation in operations:
        try:
            duration, _ = elapsed_ms(operation)
            durations[name] = duration
        except (OSError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as error:
            durations[name] = 0.0
            failures.append(f"{name}: {error}")
        except Exception as error:  # Preserve other per-user failures in the results instead of aborting a run.
            durations[name] = 0.0
            failures.append(f"{name}: unexpected {type(error).__name__}: {error}")
    return UserResult(user_id=user_id, durations_ms=durations, failures=failures)


def summarize(results: list[UserResult], config: RunConfig, elapsed_seconds: float, run_id: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    completed = sum(not result.failures for result in results)
    for task in TASK_NAMES:
        values = [result.durations_ms[task] for result in results if result.durations_ms.get(task, 0.0) > 0]
        failures = sum(any(message.startswith(f"{task}:") for message in result.failures) for result in results)
        rows.append({
            "run_id": run_id,
            "profile": config.profile,
            "api_mode": config.api_mode,
            "logical_users": config.users,
            "max_workers": config.max_workers,
            "run_elapsed_seconds": round(elapsed_seconds, 3),
            "completed_users": completed,
            "task": task,
            "samples": len(values),
            "failures": failures,
            "mean_ms": round(statistics.fmean(values), 3) if values else 0.0,
            "median_ms": round(statistics.median(values), 3) if values else 0.0,
            "p95_ms": round(percentile(values, 95), 3),
            "p99_ms": round(percentile(values, 99), 3),
            "min_ms": round(min(values), 3) if values else 0.0,
            "max_ms": round(max(values), 3) if values else 0.0,
            "throughput_users_per_second": round(config.users / elapsed_seconds, 3) if elapsed_seconds else 0.0,
        })
    return rows


def write_outputs(run_directory: Path, config: RunConfig, results: list[UserResult], summary: list[dict[str, object]], elapsed_seconds: float) -> None:
    fields = list(summary[0])
    with (run_directory / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)
    payload = {
        "configuration": {**asdict(config), "output_dir": str(config.output_dir)},
        "elapsed_seconds": elapsed_seconds,
        "users_with_failures": sum(bool(result.failures) for result in results),
        "failure_examples": [message for result in results for message in result.failures][:20],
    }
    (run_directory / "run_metadata.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def execute_run(config: RunConfig) -> Path:
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-users{config.users}"
    run_directory = config.output_dir / run_id
    (run_directory / "temporary").mkdir(parents=True, exist_ok=False)
    log_lock = threading.Lock()
    started = time.perf_counter()
    results: list[UserResult] = []
    with ThreadPoolExecutor(max_workers=config.max_workers, thread_name_prefix="load-user") as executor:
        futures = [executor.submit(run_user, user_id, config, run_directory, log_lock) for user_id in range(1, config.users + 1)]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed_seconds = time.perf_counter() - started
    shutil.rmtree(run_directory / "temporary")
    summary = summarize(results, config, elapsed_seconds, run_id)
    write_outputs(run_directory, config, results, summary, elapsed_seconds)
    print(f"Completed {config.users:,} logical users in {elapsed_seconds:.2f} seconds.")
    print(f"Results: {run_directory}")
    return run_directory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run controlled CSE 565 performance-test scenarios.")
    parser.add_argument("--users", nargs="+", type=int, choices=(100, 1_000, 10_000), default=[100],
                        help="Logical-user scenario(s) to run (default: 100).")
    parser.add_argument("--all", action="store_true", help="Run the 100, 1,000, and 10,000-user scenarios.")
    parser.add_argument("--max-workers", type=int, default=100,
                        help="Maximum active worker threads; logical users beyond this are queued (default: 100).")
    parser.add_argument("--profile", choices=tuple(PROFILES), default="standard",
                        help="Workload size; teacher-equivalent is intended only for small runs.")
    parser.add_argument("--api-mode", choices=("simulated", "real"), default="simulated",
                        help="Use a controlled simulated API response (default) or make real HTTP calls.")
    parser.add_argument("--api-url", default="https://jsonplaceholder.typicode.com/posts", help="Endpoint used with --api-mode real.")
    parser.add_argument("--request-timeout", type=float, default=10.0, help="HTTP timeout in seconds for real API mode.")
    parser.add_argument("--output-dir", type=Path, default=Path("results"), help="Directory for timestamped result folders.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_workers < 1:
        raise SystemExit("--max-workers must be at least 1.")
    if args.request_timeout <= 0:
        raise SystemExit("--request-timeout must be greater than zero.")
    users = [100, 1_000, 10_000] if args.all else args.users
    for user_count in users:
        config = RunConfig(user_count, min(args.max_workers, user_count), args.profile, args.api_mode,
                           args.api_url, args.request_timeout, args.output_dir)
        execute_run(config)


if __name__ == "__main__":
    main()
