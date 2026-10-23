"""Customer process for the Read Your Writes project."""

import grpc

import banks_pb2
import banks_pb2_grpc


PORT_BASE = 50000


class Customer:
    """Execute one customer's events while retaining its successful write IDs."""

    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = []
        self.stub = None

        # The customer sends these IDs with each request as its write dependency set.
        self.write_log = []

    def createStub(self, branch_id=None):
        """Connect to one branch; the optional default preserves client compatibility."""
        target_branch_id = self.id if branch_id is None else branch_id
        channel = grpc.insecure_channel(f"localhost:{PORT_BASE + target_branch_id}")
        self.stub = banks_pb2_grpc.RPCStub(channel)

    def executeEvents(self, events=None):
        """Send events in the order supplied by the scheduler and record responses."""
        events_to_run = self.events if events is None else events
        for event in events_to_run:
            # Course materials use both ``branch`` and ``dest`` for this field.
            destination_branch_id = event.get("branch", event.get("dest"))
            if destination_branch_id is None:
                raise ValueError("Customer event is missing its destination branch")

            # An event can target a branch different from the customer's own ID.
            self.createStub(destination_branch_id)
            request = banks_pb2.Request(
                id=event["id"],
                interface=event["interface"],
                money=event.get("money", 0),
                writeset=self.write_log,
            )
            response = self.stub.MsgDelivery(request, timeout=60)

            if event["interface"] == "query":
                result = {
                    "interface": "query",
                    "branch": destination_branch_id,
                    "balance": response.balance,
                }
            else:
                # Only successful customer writes create dependencies for later reads.
                self.write_log.append(response.write_id)
                result = {
                    "interface": event["interface"],
                    "branch": destination_branch_id,
                    "result": "success",
                }
            self.recvMsg.append(result)

        return self.recvMsg
