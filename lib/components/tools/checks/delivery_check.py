#!/usr/bin/env python3
"""Check due deliveries declared in one fenced delivery-json record (read-only)."""
import argparse
from contextlib import ExitStack
import json
import os
from pathlib import PureWindowsPath
import re
import stat
import sys


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key!r}")
        result[key] = value
    return result


def relative_parts(path):
    if (not isinstance(path, str) or not path.strip() or "\0" in path or "\\" in path
            or PureWindowsPath(path).drive or path.startswith("/") or ".." in path.split("/")):
        raise ValueError(f"expected task-relative file path: {path!r}")
    parts = [part for part in path.split("/") if part not in ("", ".")]
    if not parts or path.endswith(("/", "/.")):
        raise ValueError(f"expected file path: {path!r}")
    return parts


def read_artifact(root_fd, path, *, size_only=False):
    parts = relative_parts(path)
    with ExitStack() as opened:
        directory = root_fd
        try:
            for index, part in enumerate(parts):
                mode = os.stat(part, dir_fd=directory, follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    raise ValueError(f"symlink in path: {path!r}")
                if index < len(parts) - 1:
                    if not stat.S_ISDIR(mode):
                        return None
                    directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                    opened.callback(os.close, directory)
                else:
                    if not stat.S_ISREG(mode):
                        if stat.S_ISDIR(mode):
                            return None
                        raise ValueError(f"expected regular file: {path!r}")
                    handle = os.open(part, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
                    stream = opened.enter_context(os.fdopen(handle, "rb"))
                    info = os.fstat(handle)
                    if not stat.S_ISREG(info.st_mode):
                        raise ValueError(f"expected regular file: {path!r}")
                    return (info.st_dev, info.st_ino), (info.st_size if size_only else stream.read().decode("utf-8-sig"))
        except FileNotFoundError:
            return None


def markdown_lines(text):
    """Yield top-level lines and complete fenced blocks, excluding raw block content."""
    fence = info = raw_end = None
    body = []
    lines = text.split("\n")
    for number, line in enumerate(lines):
        line = line.removesuffix("\r")
        if number == 0 and line == "---" and any(end.rstrip() in ("---", "...") for end in lines[1:]):
            raw_end = re.compile(r"^(?:---|\.\.\.)[ \t]*$")
            continue
        if fence:
            if re.fullmatch(r" {0,3}" + fence[0] + "{" + str(len(fence)) + r",}[ \t]*", line):
                yield "block", info, "\n".join(body), start, number + 1
                fence = None
                body.clear()
            else:
                body.append(line)
            continue
        if raw_end:
            if raw_end.search(line):
                raw_end = None
            continue
        if re.match(r" {0,3}<!--", line):
            if "-->" not in line:
                raw_end = re.compile("-->")
            continue
        raw = re.match(r" {0,3}<(pre|script|style|textarea)(?:[ \t>]|$)", line, re.I)
        if raw:
            end = re.compile(r"</" + raw[1] + r">", re.I)
            if not end.search(line):
                raw_end = end
            continue
        if (re.match(r" {0,3}</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|col|"
                     r"colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|"
                     r"frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|"
                     r"menuitem|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|"
                     r"tbody|td|tfoot|th|thead|title|tr|track|ul)(?=[ \t/>]|$)", line, re.I)
                or re.fullmatch(r" {0,3}</?[A-Za-z][\w-]*(?:[ \t]+[^<>]*)?/?>[ \t]*", line)):
            raw_end = re.compile(r"^[ \t]*$")
            continue
        marker = re.fullmatch(r" {0,3}(`{3,}|~{3,})(.*)", line)
        if marker and (marker[1][0] != "`" or "`" not in marker[2]):
            fence, info = marker[1], marker[2].strip()
            if line.startswith(" ") and info == "delivery-json":
                info = ""
            start = number
            continue
        yield "line", "", line, number, number + 1
    if fence:
        yield "unclosed", info, "", start, len(lines)


def record_data(text):
    blocks = []
    for kind, info, body, start, end in markdown_lines(text):
        if info == "delivery-json":
            if kind == "unclosed":
                raise ValueError("unclosed delivery-json block")
            blocks.append((body, start, end))
    if len(blocks) != 1:
        raise ValueError("expected exactly one fenced delivery-json block")
    body, start, end = blocks[0]
    lines = text.split("\n")
    return json.loads(body, object_pairs_hook=unique_keys), ("\n".join(lines[:start]), "\n".join(lines[end:]))


def fields(obj, required, optional=()):
    if not isinstance(obj, dict) or not set(required) <= obj.keys() <= set(required) | set(optional):
        raise ValueError(f"expected fields {required}, optional {optional}")


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def validate(record):
    fields(record, ("schema", "decisions", "items"))
    if type(record["schema"]) is not int or record["schema"] != 1:
        raise ValueError("expected schema 1")
    decisions = record["decisions"]
    if not isinstance(decisions, dict) or any(not nonblank(key) or type(flag) is not bool for key, flag in decisions.items()):
        raise ValueError("decisions must map nonempty keys to booleans")
    if not isinstance(record["items"], list) or not record["items"]:
        raise ValueError("expected nonempty items array")
    identities = set()
    for item in record["items"]:
        fields(item, ("id", "title", "scope", "checks"), ("when",))
        if not nonblank(item["id"]) or item["id"] in identities or not nonblank(item["title"]):
            raise ValueError("expected unique item id and nonempty title")
        identities.add(item["id"])
        if item["scope"] not in ("authorized", "deferred", "cancelled", "needs_decision"):
            raise ValueError("invalid scope")
        if "when" in item and (not nonblank(item["when"]) or item["when"] not in decisions):
            raise ValueError("when must reference a declared decision")
        if not isinstance(item["checks"], list) or (item["scope"] == "authorized" and not item["checks"]):
            raise ValueError("expected checks array with evidence for authorized items")
        for check in item["checks"]:
            kind = check.get("type") if isinstance(check, dict) else None
            if kind == "heading":
                fields(check, ("type", "path", "level", "equals"))
                if type(check["level"]) is not int or not 1 <= check["level"] <= 6 or not nonblank(check["equals"]):
                    raise ValueError("heading needs level 1..6 and nonempty equals")
            elif kind == "text_contains":
                fields(check, ("type", "path", "value"))
                if not nonblank(check["value"]):
                    raise ValueError("text_contains needs a nonempty value")
            elif kind == "nonempty_file":
                fields(check, ("type", "path"))
            else:
                raise ValueError(f"unknown check type: {kind!r}")
            relative_parts(check["path"])


def matches(root_fd, check, record_id, record_regions):
    size_only = check["type"] == "nonempty_file"
    artifact = read_artifact(root_fd, check["path"], size_only=size_only)
    if artifact is None:
        return False
    identity, content = artifact
    if size_only:
        return identity != record_id and content > 0
    if check["type"] == "text_contains":
        if identity == record_id:
            return any(check["value"] in region for region in record_regions)
        return check["value"] in content
    for kind, _, line, _, _ in markdown_lines(content):
        if kind == "line":
            match = re.fullmatch(r" {0,3}(#{1,6})[ \t]+(.*)", line)
            if match and len(match[1]) == check["level"]:
                title = re.sub(r"[ \t]+#+[ \t]*$", "", match[2]).strip()
                if title == check["equals"]:
                    return True
    return False


def run(root_fd, path):
    artifact = read_artifact(root_fd, path)
    if artifact is None:
        raise ValueError("missing progress record")
    record_id, text = artifact
    record, record_regions = record_data(text)
    validate(record)
    results = []
    for item in record["items"]:
        status = item["scope"]
        checks = []
        if status == "authorized":
            if "when" in item and not record["decisions"][item["when"]]:
                status = "waiting"
            else:
                for check in item["checks"]:
                    passed = matches(root_fd, check, record_id, record_regions)
                    checks.append({**check, "status": "satisfied" if passed else "missing"})
                status = "missing" if any(check["status"] == "missing" for check in checks) else "satisfied"
        results.append({"id": item["id"], "title": item["title"], "status": status, "checks": checks})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", required=True)
    parser.add_argument("--record", required=True)
    args = parser.parse_args()
    try:
        root_fd = os.open(args.task_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            items = run(root_fd, args.record)
        finally:
            os.close(root_fd)
    except (ValueError, OSError, RecursionError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps({"schema": 1, "items": items}, ensure_ascii=True))
    return int(any(item["status"] == "missing" for item in items))


if __name__ == "__main__":
    sys.exit(main())
