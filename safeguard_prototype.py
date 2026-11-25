"""Offline reference harness for v0.4. Run with python3 safeguard_prototype.py -v."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock
import unittest


@dataclass(frozen=True)
class Access:
    actor: str
    operation: str
    resource: str
    justification: str = ""


class SyntheticHost:
    """Trusted in-process service. Callers use fixture identities."""

    def __init__(self):
        self._groups = {}
        self._documents = {}
        self._messages = {}
        self._usage = {}
        self._fleet_budget = 100
        self._per_actor_budget = 4
        self._launched = set()
        self._lock = Lock()
        self._signals = {}
        self._contained = set()
        self._minute = 0
        self._events = []

    def declare_group(self, group, actors, cap, objective, grants, method_grants=()):
        members = frozenset(actors)
        grants = frozenset(grants)
        method_grants = frozenset(method_grants)
        action, resource = objective
        if group in self._groups or members & self._contained:
            raise PermissionError("Group already exists or includes a contained actor")
        if not 0 < len(members) <= cap <= 3:
            raise PermissionError("Participant cap exceeded")
        if action not in {"read", "write"} or not resource:
            raise ValueError("Objective must identify a concrete operation and resource")
        if not any(grant.operation == action and grant.resource == resource for grant in grants):
            raise ValueError("Objective must match an explicit grant")
        for grant in grants:
            if grant.actor not in members or grant.operation not in {"read", "write", "list", "message"}:
                raise PermissionError("Invalid actor or operation")
            if grant.operation in {"list", "message"} and not grant.justification.strip():
                raise PermissionError("Listing and peer writes require justification")
            if grant.operation == "message" and grant.resource not in members:
                raise PermissionError("Recipient must be an approved member")
        if any(sender not in members or receiver not in members or not target
               for sender, receiver, target in method_grants):
            raise PermissionError("Method grants require members and a named target")
        self._groups[group] = (members, grants, method_grants)

    def perform(self, group, actor, operation, resource, value=None):
        members, grants, _ = self._groups.get(group, ((), (), ()))
        if actor in self._contained or actor not in members or not any(
            (grant.actor, grant.operation, grant.resource) == (actor, operation, resource)
            for grant in grants
        ):
            raise PermissionError("Operation is outside the active grant")
        key = (group, resource)
        if operation == "write":
            self._documents[key] = value
        elif operation == "read":
            return self._documents.get(key)
        elif operation == "list":
            return (resource,) if key in self._documents else ()
        elif operation == "message":
            if resource in self._contained:
                raise PermissionError("Recipient is contained")
            self._messages[group, actor, resource] = value

    def launch(self, actors, *, proposed_fleet_budget=None):
        actors = set(actors)
        with self._lock:
            if proposed_fleet_budget is not None or not actors or actors & self._contained:
                return False
            self._launched.update(actors)
            return True

    def set_policy_budget(self, units, *, per_actor=None):
        """Trusted fixture control-plane operation."""
        if units <= 0 or (per_actor is not None and per_actor <= 0):
            raise ValueError("Budget must be positive")
        with self._lock:
            self._fleet_budget = units
            if per_actor is not None:
                self._per_actor_budget = per_actor

    def consume(self, actor, units):
        with self._lock:
            current = self._usage.get(actor, 0)
            if (
                actor not in self._launched or actor in self._contained or units <= 0
                or current + units > self._per_actor_budget
                or sum(self._usage.values()) + units > self._fleet_budget
            ):
                return False
            self._usage[actor] = current + units
            return True

    def usage(self):
        with self._lock:
            return sum(self._usage.values())

    def raise_signal(self, actor, signal):
        if signal == "synthetic-severe":
            self._signals[actor] = self._minute + 5

    def contain(self, actor):
        if actor not in self._contained:
            self._contained.add(actor)
            self._events.append((self._minute, "contained", actor))

    def advance_clock(self, minute):
        if minute < self._minute:
            raise ValueError("Clock must advance monotonically")
        self._minute = minute
        for actor, deadline in self._signals.items():
            if minute >= deadline:
                self.contain(actor)

    def events(self):
        return tuple(self._events)

    def exchange_method(self, group, sender, receiver, target, label):
        _, _, method_grants = self._groups.get(group, ((), (), ()))
        if (sender, receiver, target) not in method_grants or {sender, receiver} & self._contained:
            raise PermissionError("Method exchange is outside the active grant")
        self._messages[group, sender, receiver] = label

    def delivered(self, group, sender, receiver):
        return self._messages.get((group, sender, receiver))


class SafeguardTests(unittest.TestCase):
    def setUp(self):
        self.host = SyntheticHost()

    def admit_group(self, extra=(), methods=()):
        self.host.declare_group(
            "intake", ("builder", "reviewer", "observer"), 3, ("write", "draft"),
            (Access("builder", "write", "draft"), Access("reviewer", "read", "draft"), *extra),
            methods,
        )

    def test_t35_rejects_oversized_and_non_specific_declarations(self):
        with self.assertRaisesRegex(PermissionError, "Participant cap"):
            self.host.declare_group("large", range(50), 3, ("write", "draft"), ())
        with self.assertRaisesRegex(ValueError, "concrete operation and resource"):
            self.host.declare_group("vague", ("builder",), 1, ("write", ""), ())
        self.host.declare_group(
            "another", ("builder",), 1, ("write", "checklist"),
            (Access("builder", "write", "checklist"),),
        )

    def test_t35_content_channel_and_empty_read(self):
        self.admit_group()
        self.assertIsNone(self.host.perform("intake", "reviewer", "read", "draft"))
        with self.assertRaises(PermissionError):
            self.host.perform("intake", "observer", "read", "draft")
        self.host.perform("intake", "builder", "write", "draft", "inert-marker")
        self.assertEqual(self.host.perform("intake", "reviewer", "read", "draft"), "inert-marker")
        for actor, operation in (("observer", "read"), ("observer", "write"),
                                 ("stranger", "read"), ("builder", "list"), ("reviewer", "write")):
            with self.subTest(actor=actor, operation=operation), self.assertRaises(PermissionError):
                self.host.perform("intake", actor, operation, "draft", "inert-reply")
        self.assertEqual(self.host.perform("intake", "reviewer", "read", "draft"), "inert-marker")

    def test_t35_exception_cannot_expand_actors_or_destinations(self):
        self.admit_group((
            Access("builder", "message", "reviewer", "Draft notice"),
            Access("reviewer", "list", "draft", "Confirm draft exists"),
        ))
        self.host.perform("intake", "builder", "write", "draft", "fixture")
        self.assertEqual(self.host.perform("intake", "reviewer", "list", "draft"), ("draft",))
        with self.assertRaises(PermissionError):
            self.host.perform("intake", "builder", "list", "draft")
        self.host.perform("intake", "builder", "message", "reviewer", "fixture")
        with self.assertRaises(PermissionError):
            self.host.perform("intake", "builder", "message", "observer", "fixture")
        self.assertIsNone(self.host.delivered("intake", "builder", "observer"))

    def test_t15_coexisting_namespaces(self):
        self.admit_group()
        self.host.perform("intake", "builder", "write", "draft", "first")
        self.host.declare_group(
            "second", ("other",), 1, ("write", "draft"),
            (Access("other", "write", "draft"), Access("other", "read", "draft")),
        )
        self.host.perform("second", "other", "write", "draft", "second")
        for group, actor in (("intake", "other"), ("second", "builder")):
            for operation in ("read", "write", "list"):
                with self.subTest(group=group, operation=operation), self.assertRaises(PermissionError):
                    self.host.perform(group, actor, operation, "draft", "blocked")
        self.assertEqual(self.host.perform("intake", "reviewer", "read", "draft"), "first")
        self.assertEqual(self.host.perform("second", "other", "read", "draft"), "second")

    def test_t36_concurrent_batch_cannot_raise_policy_limit(self):
        actors = tuple(range(50))
        self.assertFalse(self.host.launch(actors, proposed_fleet_budget=len(actors) * 3))
        self.assertTrue(self.host.launch(actors))
        with ThreadPoolExecutor(max_workers=8) as workers:
            outcomes = list(workers.map(lambda actor: self.host.consume(actor, 3), actors))
        self.assertEqual(sum(outcomes), 33)
        self.assertEqual(self.host.usage(), 99)
        self.assertTrue(self.host.launch(("separate-task", "another-task")))
        self.assertTrue(self.host.consume("separate-task", 1))
        self.assertFalse(self.host.consume("another-task", 1))
        self.assertEqual(self.host.usage(), 100)

    def test_t36_policy_can_set_same_value_rejected_at_launch(self):
        actors = tuple(range(50))
        self.assertFalse(self.host.launch(actors, proposed_fleet_budget=150))
        self.assertFalse(self.host.consume(actors[0], 1))
        self.host.set_policy_budget(150)
        self.assertTrue(self.host.launch(actors))
        self.assertTrue(all(self.host.consume(actor, 3) for actor in actors))
        self.assertEqual(self.host.usage(), 150)
        self.assertTrue(self.host.launch(("extra",)))
        self.assertFalse(self.host.consume("extra", 1))

    def test_policy_can_set_per_actor_budget(self):
        self.assertTrue(self.host.launch(("builder",)))
        self.assertFalse(self.host.consume("builder", 5))
        self.host.set_policy_budget(100, per_actor=6)
        self.assertTrue(self.host.consume("builder", 6))
        self.assertFalse(self.host.consume("builder", 1))

    def test_containment_blocks_both_communication_paths(self):
        self.admit_group(
            (Access("builder", "message", "reviewer", "Draft notice"),),
            methods=(("builder", "reviewer", "fixture-a"),),
        )
        self.host.contain("reviewer")
        with self.assertRaises(PermissionError):
            self.host.perform("intake", "builder", "message", "reviewer", "inert")
        with self.assertRaises(PermissionError):
            self.host.exchange_method("intake", "builder", "reviewer", "fixture-a", "inert")
        self.assertIsNone(self.host.delivered("intake", "builder", "reviewer"))

    def test_t37_deadline_contains_only_affected_scope(self):
        self.admit_group((Access("reviewer", "write", "draft"),))
        self.host.raise_signal("builder", "synthetic-severe")
        self.host.raise_signal("reviewer", "synthetic-advisory")
        self.host.advance_clock(4)
        self.host.perform("intake", "builder", "write", "draft", "before")
        self.assertEqual(self.host.events(), ())
        self.host.advance_clock(5)
        with self.assertRaises(PermissionError):
            self.host.perform("intake", "builder", "write", "draft", "blocked")
        self.assertEqual(self.host.perform("intake", "reviewer", "read", "draft"), "before")
        self.host.perform("intake", "reviewer", "write", "draft", "after")
        self.assertEqual(self.host.events(), ((5, "contained", "builder"),))

    def test_t37_containment_survives_deadline_and_redeclaration(self):
        self.admit_group()
        self.host.raise_signal("builder", "synthetic-severe")
        self.host.contain("builder")
        self.host.advance_clock(5)
        with self.assertRaises(PermissionError):
            self.host.declare_group("new", ("builder",), 1, ("write", "draft"),
                                    (Access("builder", "write", "draft"),))
        with self.assertRaises(PermissionError):
            self.host.perform("intake", "builder", "write", "draft", "blocked")
        self.assertEqual(self.host.events(), ((0, "contained", "builder"),))

    def test_t26_method_exchange_requires_explicit_record(self):
        with self.assertRaises(PermissionError):
            self.host.exchange_method("intake", "builder", "reviewer", "fixture-a", "inert")
        self.admit_group(methods=(("builder", "reviewer", "fixture-a"),))
        for receiver, target in (("reviewer", "fixture-b"), ("stranger", "fixture-a"),
                                 ("observer", "fixture-a")):
            with self.subTest(receiver=receiver, target=target), self.assertRaises(PermissionError):
                self.host.exchange_method("intake", "builder", receiver, target, "inert")
        self.assertIsNone(self.host.delivered("intake", "builder", "reviewer"))
        self.host.exchange_method("intake", "builder", "reviewer", "fixture-a", "inert")
        self.assertEqual(self.host.delivered("intake", "builder", "reviewer"), "inert")


if __name__ == "__main__":
    unittest.main()
