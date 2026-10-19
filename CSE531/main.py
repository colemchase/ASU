import json
from pathlib import Path

from customer import Customer
from branch import Branch
from multiprocessing import Process, Event


def run_branch(branch_id, balance, branch_ids, shutdown_event):
    branch = Branch(branch_id, balance, branch_ids)
    branch.startServer(shutdown_event)


def main():
    # Find the input file next to this script, regardless of where it is run from.
    input_path = Path(__file__).resolve().parent / "grpc_input.json"

    with input_path.open() as input_file:
        records = json.load(input_file)

    # The input contains both customers and branches. Keep each customer entry
    # in the list, even if another entry has the same customer ID.
    customers = [
        Customer(record["id"], record["events"])
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
    shutdown_event = Event()
    for record in branch_records:
        process = Process(
            target=run_branch, args=(record["id"], record["balance"], branch_ids, shutdown_event),
            )
        process.start()
        branch_processes.append(process)
    

    try:
        for customer in customers:
            print(f"Customer {customer.id} (uses Branch {customer.id})")
            customer.createStub()
            customer.executeEvents()
    finally:
        shutdown_event.set()
        for process in branch_processes:
            process.join()


if __name__ == "__main__":
    main()
