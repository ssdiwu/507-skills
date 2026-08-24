#!/usr/bin/env python3
"""Run every deterministic repository regression through explicit public entry points."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    cwd: Path = ROOT


def checks() -> list[Check]:
    python = sys.executable
    breakdown = ROOT / "write/507-breakdown/scripts"
    standalone_breakdown = (
        ("breakdown forced fallback", "test_forced_local_fallback.py"),
        ("breakdown image response parser", "test_image_response_parser.py"),
        ("breakdown MiniMax JSON parser", "test_minimax_json_parser.py"),
        ("breakdown understanding fixtures", "test_understanding_fixtures.py"),
        ("breakdown adaptive frames", "test_video_adaptive_frames.py"),
        ("breakdown analysis brief", "test_video_analysis_brief.py"),
        ("breakdown localization", "test_video_localization.py"),
        ("breakdown pull runtime", "test_video_pull_runtime.py"),
        ("breakdown visual relocalization", "test_visual_relocalization.py"),
    )
    result = [
        Check("PPT unit and CLI regressions", (python, "-B", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"), ROOT / "write/507-ppt/scripts"),
        Check("PPT HTML browser evidence", ("bash", "scripts/test_html.sh"), ROOT / "write/507-ppt"),
        Check("RedNote regressions", (python, "-B", "-m", "unittest", "-v", "scripts/test_render_rednote.py"), ROOT / "write/507-rednote"),
        Check("Narrate regressions", (python, "-B", "-m", "unittest", "-v", "scripts/test_voicebox_narrate.py"), ROOT / "write/507-narrate"),
        Check("Forge prose audit regressions", (python, "-B", "-m", "unittest", "-v", "test_check_prose.py"), ROOT / "write/507-forge/scripts"),
        Check("Stage spoken audit regressions", (python, "-B", "-m", "unittest", "-v", "test_check_spoken.py"), ROOT / "write/507-stage/scripts"),
        Check("Video contract regressions", (python, "-B", "-m", "unittest", "-v", "write/507-video/scripts/test_contract.py")),
        Check("Breakdown atomic publication", (python, "-B", "-m", "unittest", "-v", "test_video_pull_force.py"), breakdown),
    ]
    result.extend(Check(name, (python, "-B", filename), breakdown) for name, filename in standalone_breakdown)
    result.append(Check("Breakdown MiniMax no-key contract", (python, "-B", "test_minimax_adapter.py", "--no-key"), breakdown))
    for manifest in sorted((ROOT / "write/507-ppt/examples").glob("*.manifest.json")):
        result.append(Check(f"PPT manifest {manifest.name}", (python, "-B", "write/507-ppt/scripts/validate_manifest.py", str(manifest))))
    result.append(Check("PPT provenance report", (python, "-B", "write/507-ppt/scripts/validate_provenance.py", "--check", "write/507-ppt/examples/provenance-report.json")))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-missing-browser", action="store_true", help="explicitly permit static-only HTML checks")
    args = parser.parse_args()
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.pop("ALLOW_NO_BROWSER", None)
    if args.allow_missing_browser:
        environment["ALLOW_NO_BROWSER"] = "1"
    failures: list[str] = []
    for index, check in enumerate(checks(), start=1):
        print(f"\n[{index}] {check.name}", flush=True)
        result = subprocess.run(check.command, cwd=check.cwd, env=environment, text=True)
        if result.returncode != 0:
            failures.append(f"{check.name} (exit {result.returncode})")
    print("\nExternal gates not run: MiniMax live adapter/E2E, Voicebox authorized generation, officecli full PPTX generation, Live Photo device acceptance.")
    if failures:
        raise SystemExit("deterministic test failures:\n- " + "\n- ".join(failures))
    print("All deterministic repository checks passed.")


if __name__ == "__main__":
    main()
