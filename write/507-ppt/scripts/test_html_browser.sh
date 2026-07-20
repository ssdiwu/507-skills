#!/usr/bin/env bash
set -euo pipefail
BROWSER_ID="${1:?browser id required}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for style in swiss magazine; do
  base="file://$ROOT/examples/collaboration-$style.html"
  session="ppt-$style-$$"
  browser-act --session "$session" browser open "$BROWSER_ID" "$base" >/dev/null
  browser-act --session "$session" wait stable >/dev/null
  before="$(browser-act --session "$session" eval "document.querySelector('#status').textContent")"; [[ "$before" == *"1 / 4"* ]]
  browser-act --session "$session" keys Tab >/dev/null
  browser-act --session "$session" eval "document.activeElement.matches('button')" | grep -qi true
  browser-act --session "$session" state >/dev/null
  browser-act --session "$session" click 2 >/dev/null
  browser-act --session "$session" keys ArrowRight >/dev/null
  after="$(browser-act --session "$session" eval "document.querySelector('#status').textContent")"; [[ "$after" == *"3 / 4"* ]]
  browser-act --session "$session" eval "window.dispatchEvent(new WheelEvent('wheel',{deltaY:-100}))" >/dev/null
  wheel="$(browser-act --session "$session" eval "document.querySelector('#status').textContent")"; [[ "$wheel" == *"2 / 4"* ]]
  browser-act --session "$session" eval "window.dispatchEvent(new TouchEvent('touchstart',{touches:[new Touch({identifier:1,target:document.body,clientY:500})]}));window.dispatchEvent(new TouchEvent('touchend',{changedTouches:[new Touch({identifier:1,target:document.body,clientY:400})]}))" >/dev/null
  touch="$(browser-act --session "$session" eval "document.querySelector('#status').textContent")"; [[ "$touch" == *"3 / 4"* ]]
  browser-act --session "$session" eval "document.querySelectorAll('[role=region]').length" | grep -q 4
  browser-act --session "$session" eval "document.querySelectorAll('button').length" | grep -q 2
  browser-act --session "$session" eval "Array.from(document.querySelectorAll('.slide')).every(s=>Math.round(s.getBoundingClientRect().width)===innerWidth)" | grep -qi true
  browser-act --session "$session" eval "Array.from(document.querySelectorAll('.slide')).filter(s=>s.getAttribute('aria-hidden')==='false'&&s.dataset.current==='true').length" | grep -q 1
  browser-act --session "$session" eval "Array.from(document.querySelectorAll('button')).every(b=>b.tabIndex>=0)" | grep -qi true
  browser-act --session "$session" eval "(()=>{const L=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};const y=a=>.2126*L(a[0])+.7152*L(a[1])+.0722*L(a[2]);const ratio=(fg,bg)=>(Math.max(y(fg),y(bg))+.05)/(Math.min(y(fg),y(bg))+.05);const nums=e=>getComputedStyle(e).color.match(/\\d+/g).map(Number);const bg=e=>getComputedStyle(e.closest('.quote-box')||e.closest('.slide')).backgroundColor.match(/\\d+/g).map(Number);return ratio(nums(document.querySelector('.eyebrow')),bg(document.querySelector('.eyebrow')))>=3&&ratio(nums(document.querySelector('.quote-box small')),bg(document.querySelector('.quote-box small')))>=3})()" | grep -qi true
  browser-act session close "$session" >/dev/null
  for mode in 'static=1' 'reduced=1' 'no-webgl=1' 'fail-js=1' 'fail-init=1' 'fail-after=1&slide=1'; do
    mode_session="ppt-$style-${mode%%=*}-$$"
    browser-act --session "$mode_session" browser open "$BROWSER_ID" "$base?$mode" >/dev/null
    browser-act --session "$mode_session" wait stable >/dev/null
    browser-act --session "$mode_session" eval "document.querySelectorAll('.slide').length" | grep -q 4
    browser-act --session "$mode_session" eval "document.body.textContent.includes('从会用到会协作')" | grep -qi true
    browser-act --session "$mode_session" eval "document.documentElement.classList.contains('static')" | grep -qi true
    browser-act --session "$mode_session" eval "document.body.scrollHeight >= innerHeight*4" | grep -qi true
    browser-act --session "$mode_session" eval "Array.from(document.querySelectorAll('.slide')).every(s=>s.getBoundingClientRect().height>=innerHeight)" | grep -qi true
    browser-act --session "$mode_session" eval "Array.from(document.querySelectorAll('.slide')).every(s=>s.getAttribute('aria-hidden')==='false')" | grep -qi true
    if [[ "$mode" != 'fail-js=1' && "$mode" != 'fail-init=1' && "$mode" != 'fail-after=1&slide=1' ]]; then
      browser-act --session "$mode_session" eval "document.documentElement.dataset.overflow === 'pass'" | grep -qi true
    fi
    browser-act --session "$mode_session" state >/dev/null || true
    browser-act --session "$mode_session" click 2 >/dev/null || true
    browser-act --session "$mode_session" eval "document.querySelector('#deck').style.transform === 'none' || document.querySelector('#deck').style.transform === ''" | grep -qi true
    if [[ "$mode" != 'fail-js=1' && "$mode" != 'fail-init=1' && "$mode" != 'fail-after=1&slide=1' ]]; then
      browser-act --session "$mode_session" eval "document.documentElement.dataset.responsive === 'pass'" | grep -qi true
    fi
    browser-act session close "$mode_session" >/dev/null
  done
done
echo 'HTML browser navigation/static/failure/no-webgl/reduced-motion/a11y matrix passed'
