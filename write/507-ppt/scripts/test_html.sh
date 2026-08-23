#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME_PATH:-$(command -v google-chrome || command -v chromium || true)}"
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
if [[ -z "$CHROME" || ! -x "$CHROME" ]]; then
  echo 'HTML static fallback: browser unavailable; screenshot and browser assertions skipped'
  exit 0
fi
cd "$ROOT"
for style in swiss magazine; do
  html="$TEST_DIR/collaboration-$style.html"
  out="$TEST_DIR/screenshots/html-$style"; mkdir -p "$out"
  "$CHROME" --headless --disable-gpu --window-size=1440,900 --screenshot="$out/normal.png" "file://$html" 2>/dev/null
  for slide in 0 1 2 3; do
    "$CHROME" --headless --disable-gpu --window-size=1440,900 --screenshot="$out/slide-$((slide+1)).png" "file://$html?instant=1&slide=$slide" 2>/dev/null
  done
  "$CHROME" --headless --disable-gpu --force-prefers-reduced-motion --window-size=390,844 --screenshot="$out/reduced-mobile.png" "file://$html" 2>/dev/null
  nojs="$out/no-js-source.html"; sed 's/<script>.*<\/script>//' "$html" > "$nojs"
  "$CHROME" --headless --disable-gpu --window-size=1440,900 --screenshot="$out/no-js.png" "file://$nojs" 2>/dev/null
  "$CHROME" --headless --disable-gpu --dump-dom "file://$nojs" 2>/dev/null | grep -q '三件 AI 不能替你拥有的事'
  "$CHROME" --headless --disable-gpu --window-size=390,844 --dump-dom "file://$html?static=1" 2>/dev/null | grep -q 'data-responsive="pass"'
  "$CHROME" --headless --disable-gpu --window-size=390,844 --dump-dom "file://$html?static=1" 2>/dev/null | grep -q 'data-overflow="pass"'
  "$CHROME" --headless --disable-gpu --force-prefers-reduced-motion --window-size=390,844 --dump-dom "file://$html?static=1" 2>/dev/null | grep -q 'data-motion="reduced"'
  rm -f "$nojs"
  grep -q '@media(prefers-reduced-motion:reduce).*#hero{display:none}' "$html"
  grep -q '.js .slide{flex:0 0 100vw' "$html"
  python3 - "$out/reduced-mobile.png" <<'PY'
import sys, struct
w,h=struct.unpack('>II',open(sys.argv[1],'rb').read()[16:24]); assert (w,h)==(390,844), (w,h)
PY
  [[ $(grep -o 'role="region"' "$html" | wc -l | tr -d ' ') == 4 ]]
  [[ $(grep -o 'aria-label=' "$html" | wc -l | tr -d ' ') -ge 4 ]]
  [[ $(grep -o 'https\?://' "$html" | wc -l | tr -d ' ') == 0 ]]
done
