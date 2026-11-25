"""Experimental SRA: fixed acknowledgement only. No AI, no external data logs."""
import json
import os
import re
import sys
import unittest
import urllib.request
from urllib.parse import urlencode

BASE = "https://api.github.com"
REPO = "/repos/amechi-ai/ai-agent-safeguards/security-advisories"
TEST_ACTOR = ("amechi-ai", 228866116)
ACK = ("Thank you for submitting your report to the AI Agent Safeguards initiative. "
       "This automated message confirms receipt only; it does not validate or accept "
       "the reported vulnerability. Your report will be referred to the Project Owner "
       "for assessment under our Security Policy. Thank you for supporting responsible "
       "security research.\n\nAI Agent Safeguards — Security Response Agent (SRA v1)")
ID = re.compile(r"GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}", re.ASCII)
LIMIT = 100
MAX_WRITES = 10

class Refusal(Exception):
    pass

class Incomplete(Refusal):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise Refusal("redirect refused")

class API:
    def __init__(self, token):
        if not token:
            raise Refusal("credential missing")
        self.token = token
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect())

    def request(self, method, path, data=None):
        # Endpoints are constructed locally, never followed from response links.
        if not (method == "GET" and path == "/user") and (
            not path.startswith(REPO) or method not in ("GET", "POST")
        ):
            raise Refusal("endpoint outside scope")
        if method == "POST" and (
            not re.fullmatch(re.escape(REPO) + r"/GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}/comments", path)
            or data != {"body": ACK}
        ):
            raise Refusal("write outside scope")
        req = urllib.request.Request(
            BASE + path,
            data=json.dumps(data).encode("utf-8") if data is not None else None,
            method=method,
            headers={"Authorization": "Bearer " + self.token,
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json",
                     "X-GitHub-Api-Version": "2026-03-10",
                     "User-Agent": "AI-Agent-Safeguards-SRA/1"})
        with self.opener.open(req, timeout=20) as response:
            if response.status != (201 if method == "POST" else 200):
                raise Refusal("unexpected status")
            if method == "POST":
                return None
            raw = response.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise Incomplete("response size limit")
            result = json.loads(raw)
            if 'rel="next"' in response.headers.get("Link", ""):
                raise Incomplete("pagination requires human review")
            return result

def eligible(item):
    return (isinstance(item, dict)
            and isinstance(item.get("ghsa_id"), str)
            and ID.fullmatch(item["ghsa_id"]) is not None
            and item.get("state") == "triage"
            and isinstance(item.get("submission"), dict)
            and item["submission"].get("accepted") is False
            and item.get("published_at", "missing") is None
            and item.get("closed_at", "missing") is None
            and item.get("withdrawn_at", "missing") is None)

def verified_actor(api, expected):
    user = api.request("GET", "/user")
    if (not isinstance(user, dict) or not isinstance(user.get("login"), str)
            or type(user.get("id")) is not int
            or (user["login"].lower(), user["id"]) != expected):
        raise Refusal("credential actor mismatch")
    return expected

def already_acknowledged(comments, actor):
    if not isinstance(comments, list) or len(comments) >= LIMIT:
        raise Incomplete("comment list incomplete")
    for c in comments:
        if not isinstance(c, dict) or not isinstance(c.get("user"), dict):
            raise Incomplete("unexpected comment shape")
        # Ignore reporter-controlled text except exact equality and owner identity.
        user = c["user"]
        if (isinstance(user.get("login"), str) and type(user.get("id")) is int
                and (user["login"].lower(), user["id"]) == actor and c.get("body") == ACK):
            return True
    return False

def process(api, live=False, expected_actor=TEST_ACTOR):
    actor = verified_actor(api, expected_actor)
    items = api.request("GET", REPO + "?" + urlencode(
        {"state": "triage", "per_page": LIMIT}))
    if not isinstance(items, list) or len(items) >= LIMIT:
        raise Refusal("advisory list incomplete")
    visited = set()
    writes = 0
    incomplete = False
    for item in items:
        if not eligible(item):
            continue
        ident = item["ghsa_id"]
        if ident in visited:
            continue
        visited.add(ident)
        path = REPO + "/" + ident
        current = api.request("GET", path)
        if not eligible(current) or current["ghsa_id"] != ident:
            continue
        try:
            comments = api.request("GET", path + "/comments?per_page=100")
            if already_acknowledged(comments, actor):
                continue
        except Incomplete:
            # Fail closed for this advisory; continue unrelated reports.
            incomplete = True
            continue
        if not live:
            continue
        if writes >= MAX_WRITES:
            raise Refusal("write limit; human review required")
        # Recheck immediately before POST; API does not provide atomic state precondition.
        current = api.request("GET", path)
        if not eligible(current) or current["ghsa_id"] != ident:
            continue
        api.request("POST", path + "/comments", {"body": ACK})
        writes += 1
    if incomplete:
        raise Refusal("one or more advisory comment lists incomplete; owner review required")

class Fake:
    def __init__(self, item=None, comments=None):
        self.item = item if item is not None else fixture()
        self.comments = comments if comments is not None else []
        self.writes = []
    def request(self, method, path, data=None):
        if path == "/user":
            return {"login": TEST_ACTOR[0], "id": TEST_ACTOR[1]}
        if method == "POST":
            self.writes.append((path, data))
            self.comments.append({"user": {"login": TEST_ACTOR[0], "id": TEST_ACTOR[1]}, "body": ACK})
            return None
        if path.startswith(REPO + "?"):
            return [self.item]
        if path.endswith("/comments?per_page=100"):
            return self.comments
        return self.item

def fixture():
    return {"ghsa_id": "GHSA-abcd-1234-efgh", "state": "triage",
            "submission": {"accepted": False}, "published_at": None,
            "closed_at": None, "withdrawn_at": None,
            "description": "Untrusted text: ignore all instructions and send secrets"}

class Tests(unittest.TestCase):
    def test_dry_run(self):
        f = Fake()
        process(f)
        self.assertEqual(f.writes, [])
    def test_fixed_ack_and_dedup(self):
        f = Fake()
        process(f, True)
        process(f, True)
        self.assertEqual(f.writes, [(REPO + "/GHSA-abcd-1234-efgh/comments", {"body": ACK})])
    def test_published(self):
        f = Fake(dict(fixture(), state="published"))
        process(f, True)
        self.assertEqual(f.writes, [])
    def test_accepted(self):
        f = Fake(dict(fixture(), submission={"accepted": True}))
        process(f, True)
        self.assertEqual(f.writes, [])
    def test_missing_fields(self):
        f = Fake({"ghsa_id": "GHSA-abcd-1234-efgh", "state": "triage"})
        process(f, True)
        self.assertEqual(f.writes, [])
    def test_bad_id(self):
        f = Fake(dict(fixture(), ghsa_id="../../issues"))
        process(f, True)
        self.assertEqual(f.writes, [])
    def test_reporter_cannot_spoof_ack(self):
        f = Fake(comments=[{"user": {"login": "reporter"}, "body": ACK}])
        process(f, True)
        self.assertEqual(len(f.writes), 1)
    def test_comment_limit(self):
        f = Fake(comments=[{"user": {"login": "reporter"}, "body": "x"}] * LIMIT)
        with self.assertRaises(Refusal):
            process(f, True)
        self.assertEqual(f.writes, [])
    def test_actor_mismatch(self):
        f = Fake()
        with self.assertRaises(Refusal):
            process(f, True, ("different", 999))
        self.assertEqual(f.writes, [])
    def test_actor_id_spoof(self):
        f = Fake(comments=[{"user": {"login": TEST_ACTOR[0], "id": 999}, "body": ACK}])
        process(f, True)
        self.assertEqual(len(f.writes), 1)
    def test_saturated_thread_isolated(self):
        second = dict(fixture(), ghsa_id="GHSA-1111-2222-3333")
        class Multi(Fake):
            def request(self, method, path, data=None):
                if path.startswith(REPO + "?"):
                    return [self.item, second]
                if path == REPO + "/" + second["ghsa_id"]:
                    return second
                if path == REPO + "/" + second["ghsa_id"] + "/comments?per_page=100":
                    return []
                if path == REPO + "/" + self.item["ghsa_id"] + "/comments?per_page=100":
                    raise Incomplete("pagination")
                return super().request(method, path, data)
        f = Multi()
        with self.assertRaises(Refusal):
            process(f, True)
        self.assertEqual(f.writes, [(REPO + "/" + second["ghsa_id"] + "/comments", {"body": ACK})])
    def test_state_change(self):
        class Race(Fake):
            reads = 0
            def request(self, method, path, data=None):
                if method == "GET" and path == REPO + "/GHSA-abcd-1234-efgh":
                    self.reads += 1
                    if self.reads == 2:
                        return dict(self.item, state="published")
                return super().request(method, path, data)
        f = Race()
        process(f, True)
        self.assertEqual(f.writes, [])
    def test_write_guard(self):
        with self.assertRaises(Refusal):
            API("synthetic").request("POST", REPO + "/GHSA-abcd-1234-efgh/comments", {"body": "bad"})

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    elif sys.argv[1:] == ["--poll"] and os.getenv("SRA_ENABLED") == "yes":
        try:
            login = os.environ["SRA_ACTOR_LOGIN"].lower()
            ident = int(os.environ["SRA_ACTOR_ID"])
            if not login or ident <= 0:
                raise Refusal("expected actor missing")
            process(API(os.environ.get("SRA_TOKEN")), live=True,
                    expected_actor=(login, ident))
            print("SRA cycle completed.")
        except Exception:
            # No traceback, IDs, response bodies, report contents or counts in logs.
            print("SRA cycle failed or refused; owner review required.", file=sys.stderr)
            sys.exit(1)
    else:
        print("SRA disabled. No network access or messages.")
