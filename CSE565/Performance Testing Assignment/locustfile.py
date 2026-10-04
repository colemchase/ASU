"""Locust performance tests for the CSE 565 sample application workload.

The instructor-provided ``load_test_tasks.py`` remains unchanged. This Locust
file represents the same six workload categories with configurable sizes so
that the 100, 1,000, and 10,000-user tests can run safely on one workstation.
Metrics are emitted to Locust for every category, enabling its built-in
Failures, Response Times, and Requests Per Second reports.

Environment variables:
    CSE565_PROFILE: standard (default) or stress
    CSE565_ARTIFACT_DIR: directory for per-run temporary I/O and logs
    CSE565_API_MODE: simulated (default) or real
    CSE565_API_URL: endpoint used only when API mode is real
"""

from __future__ import annotations

import os
import random
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import gevent
from gevent.lock import Semaphore
from locust import User, between, events, task


@dataclass(frozen=True)
class WorkloadProfile:
    dataset_size: int
    database_delay_seconds: float
    api_delay_seconds: float
    file_bytes: int
    computation_limit: int


PROFILES = {
    # Used for the required 100, 1,000, and 10,000-user comparison.
    "standard": WorkloadProfile(500, 0.005, 0.010, 1_024, 500),
    # Intended for Task 5 after the baseline results have been reviewed.
    "stress": WorkloadProfile(20_000, 0.050, 0.075, 32_768, 10_000),
}

PROFILE_NAME = os.getenv("CSE565_PROFILE", "standard")
if PROFILE_NAME not in PROFILES:
    raise RuntimeError(f"Unknown CSE565_PROFILE={PROFILE_NAME!r}; choose one of {sorted(PROFILES)}.")
PROFILE = PROFILES[PROFILE_NAME]
API_MODE = os.getenv("CSE565_API_MODE", "simulated")
API_URL = os.getenv("CSE565_API_URL", "https://jsonplaceholder.typicode.com/posts")
ARTIFACT_DIR = Path(os.getenv("CSE565_ARTIFACT_DIR", "locust_results/current"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
LOG_LOCK = Semaphore()


@events.test_start.add_listener
def stop_after_requested_duration(environment, **_kwargs: object) -> None:
    """Use a gevent timer for repeatable CLI runs on the local Python runtime."""
    raw_duration = os.getenv("CSE565_DURATION_SECONDS")
    if raw_duration:
        duration = float(raw_duration)
        if duration <= 0:
            raise RuntimeError("CSE565_DURATION_SECONDS must be greater than zero.")
        gevent.spawn_later(duration, environment.runner.quit)


class SampleApplicationUser(User):
    """One Locust user that repeatedly executes the six sample-workload tasks."""

    # A wait avoids an unbounded tight loop and models think time between workflows.
    wait_time = between(0.5, 1.0)

    def on_start(self) -> None:
        self._random = random.Random(id(self))

    def _record(self, name: str, operation: Callable[[], int | str]) -> None:
        started = time.perf_counter()
        result_size = 0
        exception: Exception | None = None
        try:
            result = operation()
            result_size = len(result) if isinstance(result, (str, bytes)) else int(result)
        except Exception as error:  # Locust records the failure rather than ending the whole run.
            exception = error
        elapsed_ms = (time.perf_counter() - started) * 1_000
        self.environment.events.request.fire(
            request_type="TASK",
            name=name,
            response_time=elapsed_ms,
            response_length=result_size,
            exception=exception,
            context={"profile": PROFILE_NAME, "api_mode": API_MODE},
        )

    def _data_processing(self) -> int:
        values = [self._random.randint(1, 1_000_000) for _ in range(PROFILE.dataset_size)]
        return len(sorted(values))

    @staticmethod
    def _database_query() -> str:
        gevent.sleep(PROFILE.database_delay_seconds)
        return "Query Complete"

    @staticmethod
    def _api_request() -> int:
        if API_MODE == "simulated":
            # Do not unintentionally send thousands of requests to a public API.
            gevent.sleep(PROFILE.api_delay_seconds)
            return 200
        request = urllib.request.Request(API_URL, headers={"User-Agent": "CSE565-Locust-Test/1.0"})
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status

    def _file_io(self) -> int:
        payload = ("Load testing simulation. " * ((PROFILE.file_bytes // 25) + 1)).encode()[:PROFILE.file_bytes]
        path = ARTIFACT_DIR / f"user-{id(self)}-{self._random.randrange(1_000_000)}.txt"
        path.write_bytes(payload)
        try:
            return len(path.read_bytes())
        finally:
            path.unlink(missing_ok=True)

    @staticmethod
    def _computation() -> int:
        return sum(value * value for value in range(PROFILE.computation_limit))

    def _logging(self) -> int:
        # Intentional shared-resource behavior, corresponding to the starter's log.txt.
        with LOG_LOCK:
            with (ARTIFACT_DIR / "execution.log").open("a", encoding="utf-8") as handle:
                line = f"user={id(self)}, profile={PROFILE_NAME}, epoch={time.time():.6f}\n"
                handle.write(line)
        return len(line)

    @task
    def full_application_workflow(self) -> None:
        self._record("Data Processing", self._data_processing)
        self._record("Database Query", self._database_query)
        self._record("API Request", self._api_request)
        self._record("File I/O", self._file_io)
        self._record("Computation", self._computation)
        self._record("Logging", self._logging)
