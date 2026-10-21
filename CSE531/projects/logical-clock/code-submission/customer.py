import grpc

import banks_pb2
import banks_pb2_grpc


class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.stub = None
        self.recvMsg = []
        self.event_log = []
        self.logical_clock = 0

    def createStub(self):
        channel = grpc.insecure_channel(f"localhost:{50000 + self.id}")
        self.stub = banks_pb2_grpc.RPCStub(channel)

    def executeEvents(self, events=None):
        for event in self.events if events is None else events:
            self.logical_clock += 1
            request = banks_pb2.Request(
                id=event["id"],
                interface=event["interface"],
                money=event.get("money", 0),
                logical_clock=self.logical_clock,
            )
            if event["interface"] in ("deposit", "withdraw"):
                self.event_log.append({
                    "id": self.id,
                    "customer-request-id": event["id"],
                    "type": "customer",
                    "logical_clock": self.logical_clock,
                    "interface": event["interface"],
                    "comment": f"event_sent from customer {self.id}",
                })

            response = self.stub.MsgDelivery(request, timeout=60)
            result = (
                {"interface": "query", "balance": response.balance}
                if event["interface"] == "query"
                else {"interface": event["interface"], "result": "success"}
            )
            self.recvMsg.append(result)
        return self.recvMsg
