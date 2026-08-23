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

## Side Effects

Running the script creates or updates:

- `test_file.txt`
- `log.txt`

It also requires network access for the external API task.

## Notes For Future Codex

- If making this more submission-ready, consider adding timing metrics per task, error counts, configurable concurrency, and a CSV/Markdown report.
- Local PDF text extraction tools were not available when this README was created, so exact rubric details should be checked in the overview PDF.
