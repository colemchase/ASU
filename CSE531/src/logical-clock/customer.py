import grpc
import banks_pb2
import banks_pb2_grpc

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None

        self.logical_clock = 0

    def createStub(self):
        port = 50000 + self.id
        channel = grpc.insecure_channel(f"localhost:{port}")
        self.stub = banks_pb2_grpc.RPCStub(channel)


    def executeEvents(self, events=None):
        # The scheduler can send one event at a time to preserve global order.
        for event in self.events if events is None else events:
            self.logical_clock += 1 
            request = banks_pb2.Request(
                id=event["id"],
                interface=event["interface"],
                money=event.get("money", 0),
                logical_clock=self.logical_clock
            )
            response = self.stub.MsgDelivery(request, timeout=60)
            if event["interface"] == "query":
                result = {"interface": "query", "balance": response.balance}
            else:
                # A successful RPC means the branch finished its propagation.
                result = {"interface": event["interface"], "result": "success"}
            self.recvMsg.append(result)
        return self.recvMsg
