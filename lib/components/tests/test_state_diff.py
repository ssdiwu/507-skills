import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "state_diff.py"


class StateDiffCliTests(unittest.TestCase):
    def run_case(self, baseline, candidate, policy, raw=None):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "base.json"
            cand = Path(td) / "candidate.json"
            pol = Path(td) / "policy.json"
            base.write_text(raw[0] if raw else json.dumps(baseline), encoding="utf-8")
            cand.write_text(raw[1] if raw else json.dumps(candidate), encoding="utf-8")
            pol.write_text(raw[2] if raw else json.dumps(policy), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--baseline", str(base),
                 "--candidate", str(cand), "--policy", str(pol)],
                text=True, capture_output=True, check=False)
        self.assertEqual(proc.stderr, "")
        self.assertNotIn("Traceback", proc.stdout)
        return proc.returncode, json.loads(proc.stdout)

    def setUp(self):
        self.baseline = [{"id": "item", "state": "open", "memo": "old"}]
        self.policy = {"protectedFields": ["state"], "preserveIdentities": True}

    def test_missing_cli_arguments_are_json_error(self):
        proc = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stderr, "")
        self.assertEqual(json.loads(proc.stdout)["status"], "ERROR")

    def test_wrong_date_replacement_is_rejected(self):
        code, out = self.run_case(
            [{"id": "item", "dueDate": "2030-04-12"}],
            [{"id": "item", "dueDate": "2030-04-13"}],
            {"protectedFields": ["dueDate"]})
        self.assertEqual(code, 1)
        self.assertEqual(out["status"], "REJECT")
        self.assertIn("protected_change_not_approved", [v["type"] for v in out["violations"]])

    def test_exact_approved_change_passes(self):
        policy = {"protectedFields": ["state"], "allowedChanges": [
            {"id": "item", "field": "state", "before": "open", "after": "closed", "basis": "reviewed"}]}
        code, out = self.run_case(self.baseline, [{"id": "item", "state": "closed", "memo": "old"}], policy)
        self.assertEqual(code, 0)
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(len(out["changes"]), 1)
        self.assertEqual(len(out["sha256"]["baseline"]), 64)
        self.assertEqual(len(out["sha256"]["policy"]), 64)

    def test_candidate_protected_field_missing_rejected(self):
        code, out = self.run_case(self.baseline, [{"id": "item", "memo": "old"}], self.policy)
        self.assertEqual(code, 1)
        self.assertIn("protected_field_missing", [v["type"] for v in out["violations"]])

    def test_duplicate_ids_rejected(self):
        dup = [{"id": "item", "state": "open"}, {"id": "item", "state": "open"}]
        code, out = self.run_case(dup, self.baseline, self.policy)
        self.assertEqual(code, 2)
        self.assertEqual(out["status"], "ERROR")

    def test_ambiguous_wrapper_rejected(self):
        code, out = self.run_case(None, None, self.policy,
                                  raw=(json.dumps(self.baseline), '{"snapshot":[],"afterSnapshot":[]}', json.dumps(self.policy)))
        self.assertEqual(code, 2)
        self.assertEqual(out["status"], "ERROR")

    def test_duplicate_policy_approval_rejected(self):
        entry = {"id": "item", "field": "state", "before": "open", "after": "closed", "basis": "reviewed"}
        policy = {"protectedFields": ["state"], "allowedChanges": [entry, entry]}
        code, out = self.run_case(self.baseline, [{"id": "item", "state": "closed", "memo": "old"}], policy)
        self.assertEqual(code, 2)
        self.assertEqual(out["status"], "ERROR")

    def test_non_protected_change_is_reported_but_does_not_block(self):
        code, out = self.run_case(self.baseline, [{"id": "item", "state": "open", "memo": "new"}], self.policy)
        self.assertEqual(code, 0)
        self.assertEqual(out["changes"][0]["field"], "memo")
        self.assertFalse(out["changes"][0]["protected"])

    def test_identity_changes_can_be_reported_when_policy_allows_them(self):
        policy = {"protectedFields": ["state"], "preserveIdentities": False}
        code, out = self.run_case([], [{"id": "item", "state": "open"}], policy)
        self.assertEqual(code, 0)
        self.assertEqual(out["scope"]["identityChanges"]["added"], ["item"])
        self.assertEqual(out["changes"][0]["identityChange"], "added")

    def test_malformed_json_is_json_error_without_traceback(self):
        code, out = self.run_case(None, None, None, raw=("{", "[]", "{}"))
        self.assertEqual(code, 2)
        self.assertEqual(out["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
