import grpc
import example_pb2
import example_pb2_grpc
import time

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

    def createStub(self):
        port = 50000 + self.id
        channel = grpc.insecure_channel(f"localhost:{port}")
        self.stub = example_pb2_grpc.RPCStub(channel)


    def executeEvents(self):
        for event in self.events:
            request = example_pb2.Request(
                id=event["id"],
                interface=event["interface"],
                money=event.get("money", 0)
            )
            print(f"  Event {event["id"]}: {event["interface"]}, money={event.get("money", 0)}")
            response = self.stub.MsgDelivery(request)
            print(response)