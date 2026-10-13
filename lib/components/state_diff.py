#!/usr/bin/env python3
"""Read-only, policy-scoped comparison of record snapshots."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


class InputError(Exception):
    pass


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(message)


MISSING = object()


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    raise InputError(f"non-standard JSON constant: {value}")


def read_json(path):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc.strerror or exc}") from None
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates,
                           parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from None
    return value, hashlib.sha256(raw).hexdigest()


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def records(value, label, wrapper):
    if isinstance(value, list):
        items = value
    elif isinstance(value, dict):
        if len(value) != 1 or wrapper not in value:
            raise InputError(f"{label} must be a record list or a sole {wrapper!r} wrapper")
        items = value[wrapper]
        if not isinstance(items, list):
            raise InputError(f"{label}.{wrapper} must be a list")
    else:
        raise InputError(f"{label} must be a record list or wrapper object")
    indexed = {}
    for pos, item in enumerate(items):
        if not isinstance(item, dict):
            raise InputError(f"{label} record at index {pos} must be an object")
        ident = item.get("id")
        if not _nonempty_string(ident):
            raise InputError(f"{label} record at index {pos} needs a non-empty string id")
        if ident in indexed:
            raise InputError(f"{label} has duplicate id {ident!r}")
        indexed[ident] = item
    return indexed


def _same(a, b):
    # JSON distinguishes booleans from numbers even though Python does not.
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    return a == b


def display(value):
    return {"$missing": True} if value is MISSING else value


def parse_policy(value):
    if not isinstance(value, dict):
        raise InputError("policy must be an object")
    allowed_keys = {"protectedFields", "preserveIdentities", "allowedChanges"}
    if set(value) - allowed_keys:
        raise InputError("policy has unsupported keys")
    fields = value.get("protectedFields")
    if not isinstance(fields, list) or not fields:
        raise InputError("policy.protectedFields must be a non-empty list")
    if any(not _nonempty_string(f) for f in fields):
        raise InputError("protectedFields entries must be non-empty strings")
    if len(set(fields)) != len(fields):
        raise InputError("protectedFields must not contain duplicates")
    preserve = value.get("preserveIdentities", True)
    if not isinstance(preserve, bool):
        raise InputError("preserveIdentities must be a boolean")
    approvals = value.get("allowedChanges", [])
    if not isinstance(approvals, list):
        raise InputError("allowedChanges must be a list")
    seen = set()
    normalized = []
    required = {"id", "field", "before", "after", "basis"}
    for i, approval in enumerate(approvals):
        if not isinstance(approval, dict) or set(approval) != required:
            raise InputError(f"allowedChanges[{i}] must contain exactly id, field, before, after, basis")
        if not _nonempty_string(approval["id"]) or not _nonempty_string(approval["field"]):
            raise InputError(f"allowedChanges[{i}] needs non-empty string id and field")
        if not _nonempty_string(approval["basis"]):
            raise InputError(f"allowedChanges[{i}].basis must be a non-empty string")
        key = (approval["id"], approval["field"])
        if key in seen:
            raise InputError(f"duplicate approval for id/field {key!r}")
        seen.add(key)
        if approval["field"] not in fields:
            raise InputError(f"approval for unprotected field {approval['field']!r} is extraneous")
        normalized.append(approval)
    return fields, preserve, normalized


def compare(baseline, candidate, policy):
    fields, preserve, approvals = parse_policy(policy)
    before = records(baseline, "baseline", "snapshot")
    after = records(candidate, "candidate", "afterSnapshot")
    added = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    changes = []
    violations = []
    approved_keys = set()
    actual_by_key = {}

    if preserve and added:
        violations.append({"type": "identity_added", "ids": added})
    if preserve and removed:
        violations.append({"type": "identity_removed", "ids": removed})

    # Preserve a field-level audit trail for structural changes too. These rows
    # are reported but are governed by preserveIdentities, not change approvals.
    for ident in added:
        for field in sorted(after[ident].keys() - {"id"}):
            changes.append({"id": ident, "field": field, "before": display(MISSING),
                            "after": after[ident][field], "protected": field in fields,
                            "identityChange": "added"})
    for ident in removed:
        for field in sorted(before[ident].keys() - {"id"}):
            changes.append({"id": ident, "field": field, "before": before[ident][field],
                            "after": display(MISSING), "protected": field in fields,
                            "identityChange": "removed"})

    for ident in sorted(before.keys() & after.keys()):
        old, new = before[ident], after[ident]
        for field in sorted((old.keys() | new.keys()) - {"id"}):
            a, b = old.get(field, MISSING), new.get(field, MISSING)
            if a is not MISSING and b is not MISSING and _same(a, b):
                continue
            row = {"id": ident, "field": field, "before": display(a), "after": display(b),
                   "protected": field in fields}
            changes.append(row)
            if field in fields:
                actual_by_key[(ident, field)] = (a, b)
    for ident in sorted(after):
        for field in fields:
            if field not in after[ident]:
                violations.append({"type": "protected_field_missing", "id": ident, "field": field})

    for approval in approvals:
        key = (approval["id"], approval["field"])
        actual = actual_by_key.get(key)
        if actual is None:
            raise InputError(f"extraneous approval has no corresponding change: {key!r}")
        if actual[0] is MISSING:
            raise InputError(f"approval cannot match a missing baseline value: {key!r}")
        if not _same(actual[0], approval["before"]) or not _same(actual[1], approval["after"]):
            raise InputError(f"approval values do not exactly match observed change: {key!r}")
        approved_keys.add(key)

    for key in sorted(actual_by_key):
        if key not in approved_keys:
            violations.append({"type": "protected_change_not_approved", "id": key[0], "field": key[1]})
    return {
        "status": "PASS" if not violations else "REJECT",
        "scope": {"protectedFields": fields, "preserveIdentities": preserve,
                  "identityChanges": {"added": added, "removed": removed}},
        "changes": changes,
        "violations": violations,
    }


def main(argv=None):
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--policy", required=True)
    try:
        args = parser.parse_args(argv)
        baseline, baseline_hash = read_json(args.baseline)
        candidate, candidate_hash = read_json(args.candidate)
        policy, policy_hash = read_json(args.policy)
        result = compare(baseline, candidate, policy)
        result["sha256"] = {"baseline": baseline_hash, "candidate": candidate_hash, "policy": policy_hash}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1
    except InputError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False))
        return 2
    except Exception as exc:  # Keep malformed/unexpected input failures machine-readable.
        print(json.dumps({"status": "ERROR", "error": f"unexpected error: {exc}"}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
