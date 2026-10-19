"""Execute customer events in event-ID order and write output.json."""

import argparse
import json
from multiprocessing import Process, Queue
from queue import Empty

import grpc

import banks_pb2
import banks_pb2_grpc
from customer import Customer


def run_customer(customer_id, events, tasks, results):
    customer = Customer(customer_id, events)
    customer.createStub()
    while True:
        event = tasks.get()
        if event is None:
            break
        try:
            customer.executeEvents([event])
            results.put((event["id"], customer.recvMsg[-1], None))
        except Exception as exc:
            results.put((event["id"], None, str(exc)))
            break


def wait_for_branches(branch_ids):
    for branch_id in branch_ids:
        with grpc.insecure_channel(f"localhost:{50000 + branch_id}") as channel:
            try:
                grpc.channel_ready_future(channel).result(timeout=60)
            except grpc.FutureTimeoutError as exc:
                raise RuntimeError(f"Branch {branch_id} was not ready") from exc


def stop_branches(branch_ids):
    # A shutdown RPC sets the shared event in all branch processes.
    for branch_id in branch_ids:
        try:
            with grpc.insecure_channel(f"localhost:{50000 + branch_id}") as channel:
                stub = banks_pb2_grpc.RPCStub(channel)
                stub.MsgDelivery(banks_pb2.Request(interface="shutdown"), timeout=3)
                return
        except grpc.RpcError:
            continue
    raise RuntimeError("Could not signal the branch servers to shut down")


def build_schedule(customers, branch_ids):
    """Map each unique event ID to the customer record that owns it."""
    events_by_id = {}
    for index, customer in enumerate(customers):
        if customer["id"] not in branch_ids:
            raise ValueError(f"No branch for customer {customer['id']}")
        for event in customer["events"]:
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
    output = [{"id": customer["id"], "recv": []} for customer in customers]
    events_by_id = build_schedule(customers, branch_ids)
    remaining = [len(customer["events"]) for customer in customers]

    results = Queue()
    workers = {}
    try:
        wait_for_branches(branch_ids)
        for event_id in sorted(events_by_id):
            index, event = events_by_id[event_id]
            if index not in workers:
                tasks = Queue()
                customer = customers[index]
                process = Process(target=run_customer, args=(customer["id"], customer["events"], tasks, results))
                process.start()
                workers[index] = (process, tasks)

            process, tasks = workers[index]
            tasks.put(event)
            try:
                received_id, result, error = results.get(timeout=120)
            except Empty as exc:
                raise RuntimeError(f"Timed out waiting for event {event_id}") from exc
            if received_id != event_id or error is not None:
                raise RuntimeError(f"Customer event {event_id} failed: {error}")
            output[index]["recv"].append(result)
            remaining[index] -= 1
            if remaining[index] == 0:
                tasks.put(None)
                process.join(timeout=10)
                if process.is_alive() or process.exitcode != 0:
                    raise RuntimeError(f"Customer {customers[index]['id']} did not exit cleanly")
                tasks.close()
                del workers[index]

        with open("output.json", "w", encoding="utf-8") as output_file:
            json.dump(output, output_file, indent=2)
            output_file.write("\n")
        print(f"Wrote {len(output)} customer records to output.json.", flush=True)
    finally:
        for process, tasks in workers.values():
            tasks.put(None)
            process.join(timeout=5)
            if process.is_alive():
                process.terminate()
                process.join()
            tasks.close()
        results.close()
        stop_branches(branch_ids)


if __name__ == "__main__":
    main()
