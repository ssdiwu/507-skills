"""Locate and describe a Chrome-compatible browser without assuming PATH layout."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


MACOS_CANDIDATES = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path("/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"),
)


def find_chrome(explicit: str | Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    elif os.environ.get("CHROME_PATH"):
        candidates.append(Path(os.environ["CHROME_PATH"]).expanduser())
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        resolved = shutil.which(name)
        if resolved:
            candidates.append(Path(resolved))
    candidates.extend(MACOS_CANDIDATES)
    return next((candidate.resolve() for candidate in candidates if candidate.is_file() and os.access(candidate, os.X_OK)), None)


def chrome_version(path: Path) -> str:
    result = subprocess.run([str(path), "--version"], check=True, text=True, capture_output=True)
    return result.stdout.strip() or result.stderr.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chrome")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    browser = find_chrome(args.chrome)
    if browser is None:
        raise SystemExit("Chrome/Chromium not found; set CHROME_PATH or install a compatible browser")
    print(chrome_version(browser) if args.version else browser)


if __name__ == "__main__":
    main()
