"""gRPC branch replica for the Read Your Writes project."""

from concurrent import futures

import grpc

import banks_pb2
import banks_pb2_grpc


PORT_BASE = 50000


class Branch(banks_pb2_grpc.RPCServicer):
    """Own one replicated balance and the write records applied at this branch."""

    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance

        # Each locally originated write receives ``<branch-id>:<sequence>``.
        self.write_counter = 0

        # Maps a write ID to the operation required to replay that write.
        self.write_log = {}

        # Map peer branch IDs to their gRPC stubs so a specific peer is addressable.
        self.peer_stubs = {}
        for branch_id in branches:
            if branch_id == self.id:
                continue
            channel = grpc.insecure_channel(f"localhost:{PORT_BASE + branch_id}")
            self.peer_stubs[branch_id] = banks_pb2_grpc.RPCStub(channel)

    def apply_write(self, write_id, interface, money):
        """Apply one deposit or withdrawal and retain its replayable record."""
        amount = int(money)
        if interface == "deposit":
            self.balance += amount
        elif interface == "withdraw":
            self.balance -= amount
        else:
            raise ValueError(f"Unsupported write operation: {interface}")

        self.write_log[write_id] = {
            "interface": interface,
            "money": amount,
        }

    def tell_branches(self, request):
        """Replicate an already identified write to every peer branch."""
        for stub in self.peer_stubs.values():
            stub.MsgDelivery(request, timeout=30)

    def startServer(self, ready_event, shutdown_event):
        """Start this branch's gRPC server and wait for the shared shutdown signal."""
        self.shutdown_event = shutdown_event
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        banks_pb2_grpc.add_RPCServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{PORT_BASE + self.id}")

        server.start()
        ready_event.set()
        shutdown_event.wait()
        server.stop(grace=5).wait()

    def MsgDelivery(self, request, context):
        """Handle customer requests, branch replication, and shutdown control."""
        if request.interface == "shutdown":
            self.shutdown_event.set()
            return banks_pb2.Response(balance=self.balance)

        if request.interface == "query":
            return banks_pb2.Response(balance=self.balance)

        if request.interface in ("deposit", "withdraw"):
            # The receiving branch creates the globally unique write ID.
            self.write_counter += 1
            write_id = f"{self.id}:{self.write_counter}"
            self.apply_write(write_id, request.interface, request.money)

            propagation = banks_pb2.Request(
                id=request.id,
                interface=f"propagate_{request.interface}",
                money=request.money,
                write_id=write_id,
            )
            self.tell_branches(propagation)
            return banks_pb2.Response(balance=self.balance, write_id=write_id)

        if request.interface in ("propagate_deposit", "propagate_withdraw"):
            # A peer keeps the originating branch's ID; it must not create a new one.
            operation = request.interface.removeprefix("propagate_")
            self.apply_write(request.write_id, operation, request.money)
            return banks_pb2.Response(balance=self.balance)

        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Unknown operation")
