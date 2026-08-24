#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT
cd "$ROOT"
for style in swiss magazine; do
  python3 scripts/generate_html.py --style "$style" --output "$TEST_DIR/collaboration-$style.html"
  python3 scripts/validate_html.py "$TEST_DIR/collaboration-$style.html"
done
python3 scripts/generate_html.py --input scripts/fixtures/system-showcase.json --plan scripts/fixtures/system-showcase.visual-plan.json --candidate-only --output "$TEST_DIR/system-showcase.html"
python3 scripts/validate_html.py "$TEST_DIR/system-showcase.html"
python3 scripts/generate_html.py --input scripts/fixtures/presentation-pairwise.json --plan scripts/fixtures/presentation-pairwise.visual-plan.json --candidate-only --output "$TEST_DIR/presentation-pairwise.html"
python3 scripts/validate_html.py "$TEST_DIR/presentation-pairwise.html"
if ! CHROME="$(python3 scripts/browser_tools.py 2>/dev/null)"; then
  if [[ "${ALLOW_NO_BROWSER:-0}" == "1" ]]; then
    echo 'HTML static-only run: browser unavailable and ALLOW_NO_BROWSER=1; browser evidence was not tested'
    exit 0
  fi
  echo 'HTML browser tests require Chrome/Chromium; set CHROME_PATH or ALLOW_NO_BROWSER=1 for an explicit static-only run' >&2
  exit 1
fi
python3 scripts/html_browser_evidence.py \
  --artifact "$TEST_DIR/system-showcase.html" \
  --input scripts/fixtures/system-showcase.json \
  --plan scripts/fixtures/system-showcase.visual-plan.json \
  --chrome "$CHROME" \
  --output-dir "$TEST_DIR/system-showcase-browser-evidence"
python3 scripts/html_browser_evidence.py \
  --artifact "$TEST_DIR/presentation-pairwise.html" \
  --input scripts/fixtures/presentation-pairwise.json \
  --plan scripts/fixtures/presentation-pairwise.visual-plan.json \
  --chrome "$CHROME" \
  --output-dir "$TEST_DIR/presentation-pairwise-browser-evidence"
echo 'HTML v3 static/browser/interaction/no-JavaScript/responsive/text-flow matrix passed'
