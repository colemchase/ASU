# Client-Centric Consistency: Read Your Writes

This project extends the gRPC banking system to enforce the **Read Your
Writes** client-centric consistency guarantee. A customer may send consecutive
requests to different branch replicas, but every later read by that customer
must observe the effects of its earlier successful writes.

## Consistency Requirement

If a customer writes to one branch and later reads from another branch, the
later read must include all writes previously completed by that customer. For
example, after a customer deposits `$400` at branch 1, a query at branch 2
must return a balance that includes that deposit rather than a stale balance.

## Required Design

The implementation extends the gRPC project while preserving its file and
execution structure.

- Each branch generates a globally unique identifier for every successful
  `deposit` or `withdraw` operation and maintains a set of known write IDs
  (`writeset`) plus the associated write records.
- Each customer maintains the write IDs returned for its own successful write
  operations.
- The customer sends its current writeset with every request, including
  requests sent after moving to a different branch.
- A receiving branch compares the customer writeset with its own writeset
  before processing the request. Before returning a query result, it directly
  fetches and applies each missing write record from the originating branch.
- `query`, `deposit`, and `withdraw` may target different branches through the
  event's `branch` field.

## Input and Output

`input.json` contains one customer process, multiple branch processes, and
customer events. Each event identifies its operation, amount when applicable,
and destination branch.

The generated `output.json` must contain customer receive records in this
shape:

```json
[
  {
    "id": 1,
    "recv": [
      {"interface": "deposit", "branch": 1, "result": "success"},
      {"interface": "query", "branch": 2, "balance": 400}
    ]
  }
]
```

## Required Files

The final submission must place the following at the root of its ZIP file:

```text
protos/banks.proto
input.json
server.py
client.py
customer.py
branch.py
output.json
```

Generated protobuf Python files and `requirements.txt` may also be included.

## Run and Verify

After implementation, start the branch servers in one terminal and execute the
customer client in another:

```bash
python server.py input.json
python client.py input.json
```

The test objective is that every query reflects the customer's earlier writes,
even when the query is routed to a different branch.

## Course Materials

The project overview and written-report template are stored in
`../../projects/clientcentric-ryw/`.
