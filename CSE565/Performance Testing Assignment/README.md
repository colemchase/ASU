# CSE 565 - Performance Testing Assignment

## Purpose

Performance/load testing assignment. The folder includes a Python script that simulates concurrent users running several representative workload tasks.

## Files

- `CSE 565_Performance Testing Project_Overview Document.pdf` - assignment overview document.
- `load_test_tasks.py` - Python load simulation script.

## Current Script Behavior

`load_test_tasks.py` runs a simple multi-threaded load test with `ThreadPoolExecutor`.

Per simulated user, it executes:

- data processing: generates and sorts 100,000 random integers
- simulated database query: sleeps for 0.5 seconds
- external API request: calls `https://jsonplaceholder.typicode.com/posts`
- file I/O: writes and reads `test_file.txt`
- computation: sums squares for numbers 0 through 9999
- logging: appends a timestamp to `log.txt`

The script currently defaults to `concurrent_users = 10`, prints total execution time, and prints sample results for two users.

## How To Run

```bash
python3 load_test_tasks.py
```

## Scalable Benchmark Runner

`load_test_tasks.py` is instructor-provided and has not been changed. The separate
`performance_benchmark.py` runner supports the required 100-, 1,000-, and
10,000-logical-user scenarios while bounding the number of active threads.

Run the three scenarios with a consistent controlled workload:

```bash
python3 performance_benchmark.py --all --profile standard --max-workers 100
```

The runner's default `simulated` API mode is deliberate: it prevents an all-scenario
run from issuing 11,100 requests to the public JSONPlaceholder service. To test a
real endpoint that you are authorized to load, use `--api-mode real` and set an
appropriate `--api-url` and `--request-timeout`.

Each scenario writes a timestamped folder in `results/` with:

- `summary.csv`: per-task mean, median, P95, P99, min/max latency, failures, and throughput.
- `run_metadata.json`: exact workload and run configuration plus any failure examples.
- `execution.log`: synchronized per-user execution records.

Useful commands:

```bash
# Validate the harness quickly before a full measured run.
python3 performance_benchmark.py --users 100 --profile quick --max-workers 25

# Run one required scenario.
python3 performance_benchmark.py --users 1000 --profile standard --max-workers 100

# Approximate the starter workload; use this only for small scenarios.
python3 performance_benchmark.py --users 100 --profile teacher-equivalent --max-workers 10
```

`Performance_Testing_Report.tex` is the APA-style LaTeX report template. It follows
the title-page, double-spacing, paragraph-indent, table/figure, and reference style
used by the other CSE 565 project reports. Fill its results tables only from the
generated `summary.csv` files.

## Side Effects

Running the script creates or updates:

- `test_file.txt`
- `log.txt`

It also requires network access for the external API task.

## Notes For Future Codex

- If making this more submission-ready, consider adding timing metrics per task, error counts, configurable concurrency, and a CSV/Markdown report.
- Local PDF text extraction tools were not available when this README was created, so exact rubric details should be checked in the overview PDF.
