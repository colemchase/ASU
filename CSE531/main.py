import json
from pathlib import Path

from customer import Customer
from branch import Branch


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

    branches = [
        Branch(record["id"], record["balance"], branch_ids)
        for record in records
        if record["type"] == "branch"
    ]

    for customer in customers:
        print(f"Customer {customer.id} (uses Branch {customer.id})")
        for event in customer.events:
            event_id = event["id"]
            operation = event["interface"]
            money = event.get("money")  # Queries do not have a money field.
            print(f"  Event {event_id}: {operation}, money={money}")


if __name__ == "__main__":
    main()
