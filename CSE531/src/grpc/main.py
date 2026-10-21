import json
from pathlib import Path

from customer import Customer
from branch import Branch
from multiprocessing import Process, Event


def run_branch(branch_id, balance, branch_ids, ready_event, shutdown_event):
    branch = Branch(branch_id, balance, branch_ids)
    branch.startServer(ready_event, shutdown_event)


def run_customer(customer_id, events):
    customer = Customer(customer_id, events)
    customer.createStub()
    customer.executeEvents()


def main():
    # Find the input file next to this script, regardless of where it is run from.
    input_path = Path(__file__).resolve().parent / "grpc_input.json"

    with input_path.open() as input_file:
        records = json.load(input_file)

    customers = [
        record
        for record in records
        if record["type"] == "customer"
    ]

    branch_ids = [
        record["id"]
        for record in records
        if record["type"] == "branch"
    ]

    branch_records = [
        record
        for record in records
        if record["type"] == "branch"
    ]


    branch_processes = []
    ready_events = []
    shutdown_event = Event()
    for record in branch_records:
        ready_event = Event()
        process = Process(
            target=run_branch, args=(record["id"], record["balance"], branch_ids, ready_event, shutdown_event),
            )
        process.start()
        ready_events.append(ready_event)
        branch_processes.append(process)

    

    try:
        for ready_event in ready_events:
            if not ready_event.wait(timeout=30):
                raise RuntimeError("A branch server did not start in time")
        for customer in customers:
            print(f"Customer {customer['id']} (uses Branch {customer['id']})")

            process = Process(
                target=run_customer,
                args=(customer["id"], customer["events"]),
            )
            process.start()
            process.join()

            if process.exitcode != 0:
                raise RuntimeError(f"Customer {customer['id']} failed")
    finally:
        shutdown_event.set()
        for process in branch_processes:
            process.join()


if __name__ == "__main__":
    main()
