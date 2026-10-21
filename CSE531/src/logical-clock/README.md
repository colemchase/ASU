# CSE 531 Logical Clock Project

This project extends the gRPC banking system with Lamport logical clocks. Each
customer and branch owns one scalar clock, while branches replicate every
deposit and withdrawal to every peer branch.

## Run

Install the required packages, then start the servers in one terminal and the
client in another:

```bash
python server.py input.json
python client.py input.json
```

The client writes `output.json` and signals the server processes to stop when
all requests have completed.

## Lamport Clock Rules

- Before a customer or branch sends an application message, it increments its
  own clock and attaches that value to the request.
- When a branch receives an application message, it sets its clock to
  `max(local_clock, received_clock) + 1` before handling the operation.
- A branch increments again for every individual propagation send, so each
  peer receives a distinct event timestamp.

The `get_events` and `shutdown` RPCs are collection/control operations; they
do not represent banking events and therefore do not alter the application
event log.

## Output

`output.json` contains the three sections required by the project overview in
this order:

1. Per-customer event logs
2. Per-branch event logs
3. A flat log of all events triggered by each deposit or withdrawal request

The assignment example spells the propagation interface `propogate_*`; this
project deliberately retains that spelling for compatibility with the expected
output.

## Verification

Run the focused tests with:

```bash
python -m unittest discover -s tests -v
```

The supplied input produces 8 customer events, 56 branch events, and 64 flat
per-request events.
