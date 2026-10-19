# CSE 531 gRPC banking project

This project models one shared account replicated across bank branches. Each
customer uses the branch with the same ID. A deposit or withdrawal changes that
branch's balance and is propagated through gRPC to every other branch. A query
returns the contacted branch's local balance.

## Setup and execution

Use Python 3.13 and install the assignment's required library versions:

```sh
python -m pip install -r requirements.txt
```

In one terminal, start the branch servers and leave the terminal open:

```sh
python server.py input.json
```

Once the servers report that they are ready, run the client in another terminal:

```sh
python client.py input.json
```

The client writes `output.json` in its current directory and signals the branch
servers to shut down. Both commands take the same input JSON path; for example,
in the original project folder it may be named `grpc_input.json` instead.

## Design

- `protos/example.proto` defines the unary `MsgDelivery` RPC and its request
  and response messages. The generated `example_pb2.py` and
  `example_pb2_grpc.py` modules are included.
- `server.py` starts a separate process and gRPC server for each branch.
  Branch ID `n` listens on port `50000 + n` on the local machine.
- `client.py` associates each event ID with its customer record and executes
  events in ascending event-ID order. Customer records have separate processes;
  the client waits for each event to complete before sending the next one.
- `customer.py` sends requests to its matching branch and records successful
  responses. `branch.py` handles queries, customer updates, and propagated
  updates. Propagated updates are applied locally and are not broadcast again.
- Each outgoing propagation call is synchronous. A customer update returns only
  after the contacted branch has received successful responses from its peers.
  The output preserves one entry per input customer record, including repeated
  customer IDs in the supplied input.

The assignment assumes no concurrent account updates. This implementation also
assumes branch servers are available during processing; it does not provide
rollback or recovery if a propagation fails partway through. The specification
does not define an insufficient-funds rule, so none is added. RPC errors stop the
run rather than being recorded as successful events.

## Verification

Run the focused unit tests without starting servers:

```sh
python -m unittest discover -s tests -v
```

The `tests/interleaved.json` fixture can be used with the two commands above in
place of `input.json` to check globally interleaved event IDs. Run the client
from a separate directory if you do not want to overwrite your `output.json`.
The supplied full input was also run end-to-end: its 100 customer records
produced 200 responses, all matching the expected progression from 400 to 900
and back to 400.

To regenerate the protobuf modules after changing the service definition:

```sh
python -m grpc_tools.protoc -Iprotos --python_out=. --grpc_python_out=. protos/example.proto
```
