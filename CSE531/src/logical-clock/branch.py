import grpc
import banks_pb2
import banks_pb2_grpc
from concurrent import futures

class Branch(banks_pb2_grpc.RPCServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        
        self.stubList = list()

        self.recvMsg = list()

        self.logical_clock = 0

        # iterate the processID of the branches
        # the list of process IDs of the branches
        self.branches = branches
        for branch_id in self.branches:
            if branch_id == self.id:
                continue
            port = 50000 + branch_id
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = banks_pb2_grpc.RPCStub(channel)
            self.stubList.append(stub)

    def tellBranches(self, request):
        for stub in self.stubList:
            self.logical_clock += 1
            if request.interface == "deposit":
                propagation = banks_pb2.Request(
                    id=request.id,
                    interface="propagate_deposit",
                    money=request.money,
                    logical_clock=self.logical_clock
                )
            else:
                propagation = banks_pb2.Request(
                    id=request.id,
                    interface="propagate_withdraw",
                    money=request.money,
                    logical_clock=self.logical_clock
                )
            stub.MsgDelivery(propagation, timeout=30)

    def startServer(self, ready_event, shutdown_event):
        self.shutdown_event = shutdown_event
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        banks_pb2_grpc.add_RPCServicer_to_server(self, server)

        port = 50000 + self.id
        server.add_insecure_port(f"[::]:{port}")

        server.start()
        ready_event.set()
        shutdown_event.wait()       # Wait until main signals us to stop.
        server.stop(grace=5).wait() # Allow active calls time to finish.

    def MsgDelivery(self, request, context):
        self.logical_clock = max(self.logical_clock, request.logical_clock) + 1
        if request.interface == "shutdown":
            # All branch processes share this event; the client signals it once
            # after the scheduled customer events have completed.
            self.shutdown_event.set()
        elif request.interface == "deposit":
            self.balance += int(request.money)
            self.tellBranches(request)
        elif request.interface == "withdraw":
            self.balance -= int(request.money)
            self.tellBranches(request)
        elif request.interface == "propagate_deposit":
            self.balance += int(request.money)
        elif request.interface == "propagate_withdraw":
            self.balance -= int(request.money)
        elif request.interface != "query":
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Unknown operation")
        return banks_pb2.Response(balance=self.balance)
