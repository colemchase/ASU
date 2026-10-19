import grpc
import example_pb2
import example_pb2_grpc

class Branch(example_pb2_grpc.RPCServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        
        # the list of Client stubs to communicate with the branches
        self.stubList = list()

        # a list of received messages used for debugging purpose
        self.recvMsg = list()

        # iterate the processID of the branches
        # the list of process IDs of the branches
        self.branches = branches
        for branch_id in self.branches:
            if branch_id == self.id:
                continue
            port = 50000 + branch_id
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = example_pb2_grpc.RPCStub(channel)
            self.stubList.append(stub)

    # TODO: students are expected to process requests from both Client and Branch
    def MsgDelivery(self,request, context):
        pass