"""Start one gRPC server process for each branch in the input file."""

import argparse
import json
from multiprocessing import Event, Process

from branch import Branch


def run_branch(branch_id, balance, branch_ids, ready_event, shutdown_event):
    branch = Branch(branch_id, balance, branch_ids)
    branch.startServer(ready_event, shutdown_event)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input JSON file")
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as input_file:
        records = json.load(input_file)

    branches = [record for record in records if record["type"] == "branch"]
    branch_ids = [branch["id"] for branch in branches]
    if not branches or len(set(branch_ids)) != len(branch_ids):
        raise ValueError("Input must contain branches with unique IDs")

    shutdown_event = Event()
    processes = []
    ready_events = []
    try:
        for branch in branches:
            ready = Event()
            process = Process(
                target=run_branch,
                args=(branch["id"], branch["balance"], branch_ids, ready, shutdown_event),
            )
            process.start()
            processes.append(process)
            ready_events.append(ready)

        for branch, process, ready in zip(branches, processes, ready_events):
            if not ready.wait(timeout=60):
                raise RuntimeError(f"Branch {branch['id']} failed to start (exit code {process.exitcode})")
        print(f"All {len(branches)} branch servers are ready.", flush=True)

        while not shutdown_event.wait(timeout=1):
            for process in processes:
                if process.exitcode is not None:
                    raise RuntimeError(f"A branch process exited unexpectedly: {process.exitcode}")
    finally:
        shutdown_event.set()
        for process in processes:
            process.join(timeout=10)
            if process.is_alive():
                process.terminate()
                process.join()


if __name__ == "__main__":
    main()
