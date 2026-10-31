#!/bin/zsh
# usage: fill2.sh <index of visible input/textarea> <text>  (focus by script, paste by keyboard)
D=$(dirname $0)
$D/sfront.sh >/dev/null
F=$($D/sjs.sh "(()=>{const e=[...document.querySelectorAll('input,textarea')].filter(e=>e.getBoundingClientRect().width>0)[$1];if(!e)return 'NOEL';e.scrollIntoView({block:'center'});e.focus();return document.activeElement===e?'ok':'nofocus'})()")
[ "$F" = "ok" ] || { echo "focus $1: $F"; exit 1; }
printf "%s" "$2" | pbcopy
osascript -e 'tell application "System Events"' -e 'keystroke "a" using command down' -e 'delay 0.15' -e 'keystroke "v" using command down' -e 'end tell' >/dev/null
sleep 0.5
