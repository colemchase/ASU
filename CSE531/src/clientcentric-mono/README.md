# Client-Centric Consistency: Monotonic Writes

This project extends the gRPC banking system to enforce **Monotonic Writes**
client-centric consistency. A customer's successive writes must be applied in
the same order at every branch replica, even when the customer changes the
branch handling the next request.

## Consistency Requirement

For a process and data item, each write must complete before that same process
performs its next write. For example, if a customer deposits `$200` at branch 1
and then deposits `$300` at branch 2, branch 2 must observe and apply the
`$200` write before accepting the `$300` write. The final replicated balance
must therefore be `$500`, not `$300`.

## Required Design

The implementation will extend the gRPC project while preserving its file and
execution structure.

- Each branch generates an identifier for every successful `deposit` or
  `withdraw` operation and maintains the write IDs it knows (`writeset`).
- The customer stores the IDs of its completed writes in its own writeset.
- The customer sends its current writeset with every request to a branch.
- Before a branch accepts a new customer write, it compares the received
  writeset with its local writeset and ensures all earlier writes from that
  customer are present first.
- The implementation must preserve the customer's write order when requests
  move between branches.
- Queries may be routed to another branch after the write sequence and should
  reflect the correctly ordered final balance.

## Input and Output

`input.json` contains one customer, multiple branch replicas, and customer
events. The overview calls the destination field `dest`; the provided input
uses `branch`. The implementation should support the field used by the test
input and can safely normalize both names.

The required `output.json` is a list of final balances by customer:

```json
[
  {"id": 1, "balance": 0}
]
```

For the overview example, the customer deposits `$400`, withdraws `$400` at a
different branch, and then queries that branch. The correct final balance is
therefore `0`; a stale result of `400` demonstrates a Monotonic Writes failure.

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

The test objective is that every returned balance reflects the customer's
writes in order across all branches.

## Course Materials

The project overview and written-report template are stored in
`../../projects/clientcentric-mono/`.
