import json
from concurrent import futures

import grpc

import banks_pb2
import banks_pb2_grpc


class Branch(banks_pb2_grpc.RPCServicer):
    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.logical_clock = 0
        self.event_log = []
        self.stubList = []

        for branch_id in branches:
            if branch_id == self.id:
                continue
            channel = grpc.insecure_channel(f"localhost:{50000 + branch_id}")
            self.stubList.append((branch_id, banks_pb2_grpc.RPCStub(channel)))

    def record_event(self, request, interface, comment):
        self.event_log.append({
            "id": self.id,
            "customer-request-id": request.id,
            "type": "branch",
            "logical_clock": self.logical_clock,
            "interface": interface,
            "comment": comment,
        })

    def tellBranches(self, request):
        propagation_interface = (
            "propogate_withdraw"
            if request.interface == "withdraw"
            else "propogate_deposit"
        )
        for branch_id, stub in self.stubList:
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
        server.add_insecure_port(f"[::]:{50000 + self.id}")
        server.start()
        ready_event.set()
        shutdown_event.wait()
        server.stop(grace=5).wait()

    def MsgDelivery(self, request, context):
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

        self.logical_clock = max(self.logical_clock, request.logical_clock) + 1
        if request.interface == "query":
            return banks_pb2.Response(balance=self.balance)

        if request.interface == "deposit":
            self.balance += int(request.money)
            self.record_event(request, "deposit", f"event_recv from customer {self.id}")
            self.tellBranches(request)
        elif request.interface == "withdraw":
            self.balance -= int(request.money)
            self.record_event(request, "withdraw", f"event_recv from customer {self.id}")
            self.tellBranches(request)
        elif request.interface == "propogate_deposit":
            self.balance += int(request.money)
            self.record_event(request, request.interface, f"event_recv from branch {request.sender_branch_id}")
        else:
            self.balance -= int(request.money)
            self.record_event(request, request.interface, f"event_recv from branch {request.sender_branch_id}")

        return banks_pb2.Response(balance=self.balance)
