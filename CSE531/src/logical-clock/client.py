"""Execute customer events and write the Logical Clock event log."""

import argparse
import json

import grpc

import banks_pb2
import banks_pb2_grpc
from customer import Customer


def wait_for_branches(branch_ids):
    for branch_id in branch_ids:
        with grpc.insecure_channel(f"localhost:{50000 + branch_id}") as channel:
            try:
                grpc.channel_ready_future(channel).result(timeout=60)
            except grpc.FutureTimeoutError as exc:
                raise RuntimeError(f"Branch {branch_id} was not ready") from exc


def stop_branches(branch_ids):
    for branch_id in branch_ids:
        try:
            with grpc.insecure_channel(f"localhost:{50000 + branch_id}") as channel:
                banks_pb2_grpc.RPCStub(channel).MsgDelivery(
                    banks_pb2.Request(interface="shutdown"), timeout=3
                )
                return
        except grpc.RpcError:
            continue
    raise RuntimeError("Could not signal the branch servers to shut down")


def get_branch_events(branch_ids):
    branch_sections = []
    all_events = []
    for branch_id in branch_ids:
        with grpc.insecure_channel(f"localhost:{50000 + branch_id}") as channel:
            response = banks_pb2_grpc.RPCStub(channel).MsgDelivery(
                banks_pb2.Request(interface="get_events"), timeout=10
            )
            events = json.loads(response.event_log_json)
            branch_sections.append({
                "id": branch_id,
                "type": "branch",
                "events": [event_details(event) for event in events],
            })
            all_events.extend(events)
    return branch_sections, all_events


def request_id(event):
    """Read either the gRPC-project or logical-clock-project request ID."""
    for field, value in event.items():
        if field.strip() in ("id", "customer-request-id", "customer-requests"):
            return int(value)
    raise ValueError("Customer request is missing customer-request-id")


def customer_requests(customer):
    requests = customer.get("customer-requests", customer.get("events", []))
    return [{
        "id": request_id(request),
        "interface": request["interface"],
        "money": request.get("money", 0),
    } for request in requests]


def event_details(event):
    return {
        "customer-request-id": event["customer-request-id"],
        "logical_clock": event["logical_clock"],
        "interface": event["interface"],
        "comment": event["comment"],
    }


def build_schedule(customers, branch_ids):
    """Map each unique event ID to the customer record that owns it."""
    events_by_id = {}
    for index, customer in enumerate(customers):
        if customer["id"] not in branch_ids:
            raise ValueError(f"No branch for customer {customer['id']}")
        for event in customer_requests(customer):
            event_id = event["id"]
            if event_id in events_by_id:
                raise ValueError(f"Duplicate event ID: {event_id}")
            if event["interface"] not in ("query", "deposit", "withdraw"):
                raise ValueError(f"Unknown customer operation: {event['interface']}")
            events_by_id[event_id] = (index, event)
    return events_by_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input JSON file")
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as input_file:
        records = json.load(input_file)

    customers = [record for record in records if record["type"] == "customer"]
    branch_ids = [record["id"] for record in records if record["type"] == "branch"]
    if not branch_ids:
        raise ValueError("Input must contain at least one branch")

    schedule = build_schedule(customers, branch_ids)
    customer_processes = [
        Customer(customer["id"], customer_requests(customer))
        for customer in customers
    ]
    try:
        wait_for_branches(branch_ids)
        for event_id in sorted(schedule):
            customer_index, event = schedule[event_id]
            customer = customer_processes[customer_index]
            if customer.stub is None:
                customer.createStub()
            customer.executeEvents([event])

        customer_sections = [{
            "id": customer.id,
            "type": "customer",
            "events": [event_details(event) for event in customer.event_log],
        } for customer in customer_processes]
        customer_events = [event for customer in customer_processes for event in customer.event_log]
        branch_sections, branch_events = get_branch_events(branch_ids)
        request_events = customer_events + branch_events
        request_events.sort(key=lambda event: (
            event["customer-request-id"],
            event["logical_clock"],
            event["id"],
        ))
        with open("output.json", "w", encoding="utf-8") as output_file:
            json.dump(customer_sections + branch_sections + request_events, output_file, indent=2)
            output_file.write("\n")
        print(f"Wrote {len(request_events)} logical-clock events to output.json.", flush=True)
    finally:
        stop_branches(branch_ids)


if __name__ == "__main__":
    main()
