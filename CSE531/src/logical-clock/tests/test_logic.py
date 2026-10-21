"""Focused tests for banking operations and event scheduling."""

import unittest
from unittest.mock import Mock, patch

import grpc

import banks_pb2
from branch import Branch
from client import build_schedule
from customer import Customer


class BranchTests(unittest.TestCase):
    def setUp(self):
        # Exercise the handler directly, without opening sockets.
        with patch("branch.grpc.insecure_channel"), patch("branch.banks_pb2_grpc.RPCStub") as stub:
            self.peer = Mock()
            stub.return_value = self.peer
            self.branch = Branch(1, 400, [1, 2])
        self.context = Mock()

    def deliver(self, operation, money=0):
        request = banks_pb2.Request(id=7, interface=operation, money=money)
        return self.branch.MsgDelivery(request, self.context)

    def test_query_returns_balance_without_propagation(self):
        self.assertEqual(self.deliver("query").balance, 400)
        self.peer.MsgDelivery.assert_not_called()

    def test_deposit_updates_and_propagates(self):
        self.assertEqual(self.deliver("deposit", 10).balance, 410)
        request = self.peer.MsgDelivery.call_args.args[0]
        self.assertEqual((request.id, request.interface, request.money), (7, "propagate_deposit", 10))

    def test_withdraw_updates_and_propagates(self):
        self.assertEqual(self.deliver("withdraw", 10).balance, 390)
        request = self.peer.MsgDelivery.call_args.args[0]
        self.assertEqual((request.id, request.interface, request.money), (7, "propagate_withdraw", 10))

    def test_propagated_deposit_updates_without_rebroadcast(self):
        self.assertEqual(self.deliver("propagate_deposit", 10).balance, 410)
        self.peer.MsgDelivery.assert_not_called()

    def test_propagated_withdraw_updates_without_rebroadcast(self):
        self.assertEqual(self.deliver("propagate_withdraw", 10).balance, 390)
        self.peer.MsgDelivery.assert_not_called()

    def test_unknown_operation_aborts(self):
        self.context.abort.side_effect = ValueError("unknown operation")
        with self.assertRaises(ValueError):
            self.deliver("unknown")
        self.context.abort.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT, "Unknown operation")


class CustomerTests(unittest.TestCase):
    def test_successful_responses_match_output_schema(self):
        events = [
            {"id": 1, "interface": "deposit", "money": 10},
            {"id": 2, "interface": "query"},
            {"id": 3, "interface": "withdraw", "money": 5},
        ]
        customer = Customer(1, events)
        customer.stub = Mock()
        customer.stub.MsgDelivery.side_effect = [
            banks_pb2.Response(balance=410),
            banks_pb2.Response(balance=410),
            banks_pb2.Response(balance=405),
        ]
        self.assertEqual(customer.executeEvents(), [
            {"interface": "deposit", "result": "success"},
            {"interface": "query", "balance": 410},
            {"interface": "withdraw", "result": "success"},
        ])
        self.assertEqual(customer.stub.MsgDelivery.call_count, 3)


class ScheduleTests(unittest.TestCase):
    def test_interleaved_events_are_sorted_globally(self):
        customers = [
            {"id": 1, "events": [{"id": 4, "interface": "query"}, {"id": 1, "interface": "query"}]},
            {"id": 2, "events": [{"id": 3, "interface": "query"}, {"id": 2, "interface": "query"}]},
        ]
        schedule = build_schedule(customers, [1, 2])
        self.assertEqual([(event_id, schedule[event_id][0]) for event_id in sorted(schedule)],
                         [(1, 0), (2, 1), (3, 1), (4, 0)])

    def test_duplicate_event_ids_are_rejected(self):
        customers = [{"id": 1, "events": [
            {"id": 1, "interface": "query"}, {"id": 1, "interface": "query"}
        ]}]
        with self.assertRaisesRegex(ValueError, "Duplicate event ID"):
            build_schedule(customers, [1])

    def test_missing_customer_branch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "No branch"):
            build_schedule([{"id": 2, "events": []}], [1])


if __name__ == "__main__":
    unittest.main()
