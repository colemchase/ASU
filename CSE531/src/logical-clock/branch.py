"""Branch gRPC service with a Lamport logical clock."""

import json
from concurrent import futures

import grpc

import banks_pb2
import banks_pb2_grpc


PORT_BASE = 50000


class Branch(banks_pb2_grpc.RPCServicer):
    """Own a replicated branch balance, event log, and Lamport clock."""

    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.logical_clock = 0
        self.event_log = []
        self.peer_stubs = []

        for branch_id in branches:
            if branch_id == self.id:
                continue
            channel = grpc.insecure_channel(f"localhost:{PORT_BASE + branch_id}")
            self.peer_stubs.append((branch_id, banks_pb2_grpc.RPCStub(channel)))

    def record_event(self, request, interface, comment):
        self.event_log.append({
            "id": self.id,
            "customer-request-id": request.id,
            "type": "branch",
            "logical_clock": self.logical_clock,
            "interface": interface,
            "comment": comment,
        })

    def tell_branches(self, request):
        """Send one timestamped propagation event to every peer branch."""
        propagation_interface = (
            # The assignment's supplied output intentionally uses this spelling.
            "propogate_withdraw"
            if request.interface == "withdraw"
            else "propogate_deposit"
        )
        for branch_id, stub in self.peer_stubs:
            # A send is a Lamport event, so each peer gets a distinct timestamp.
            self.logical_clock += 1
            propagation = banks_pb2.Request(
                id=request.id,
                interface=propagation_interface,
                money=request.money,
                logical_clock=self.logical_clock,
                sender_branch_id=self.id,
            )
            self.record_event(
                propagation,
                propagation.interface,
                f"event_sent to branch {branch_id}",
            )
            stub.MsgDelivery(propagation, timeout=30)

    def startServer(self, ready_event, shutdown_event):
        self.shutdown_event = shutdown_event
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        banks_pb2_grpc.add_RPCServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{PORT_BASE + self.id}")
        server.start()
        ready_event.set()
        shutdown_event.wait()
        server.stop(grace=5).wait()

    def MsgDelivery(self, request, context):
        """Handle control, customer, and propagation messages."""
        if request.interface == "get_events":
            return banks_pb2.Response(
                balance=self.balance,
                event_log_json=json.dumps(self.event_log),
            )
        if request.interface == "shutdown":
            self.shutdown_event.set()
            return banks_pb2.Response(balance=self.balance)
        if request.interface not in (
            "query",
            "deposit",
            "withdraw",
            "propogate_deposit",
            "propogate_withdraw",
        ):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Unknown operation")

        # Lamport receive rule: advance beyond both the local and sent time.
        self.logical_clock = max(self.logical_clock, request.logical_clock) + 1
        if request.interface == "query":
            return banks_pb2.Response(balance=self.balance)

        if request.interface == "deposit":
            self.balance += int(request.money)
            self.record_event(request, "deposit", f"event_recv from customer {self.id}")
            self.tell_branches(request)
        elif request.interface == "withdraw":
            self.balance -= int(request.money)
            self.record_event(request, "withdraw", f"event_recv from customer {self.id}")
            self.tell_branches(request)
        elif request.interface == "propogate_deposit":
            self.balance += int(request.money)
            self.record_event(request, request.interface, f"event_recv from branch {request.sender_branch_id}")
        else:
            self.balance -= int(request.money)
            self.record_event(request, request.interface, f"event_recv from branch {request.sender_branch_id}")

        return banks_pb2.Response(balance=self.balance)
