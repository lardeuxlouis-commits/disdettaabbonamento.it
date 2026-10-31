#!/bin/zsh
D=$(dirname $0); $D/sfront.sh >/dev/null
F=$($D/sjs.sh "(()=>{const e=[...document.querySelectorAll('input,textarea')].filter(e=>e.getBoundingClientRect().width>0)[$1];if(!e)return 'NOEL';e.scrollIntoView({block:'center'});e.focus();return document.activeElement===e?'ok':'nofocus'})()")
[ "$F" = "ok" ] || { echo "focus $1: $F"; exit 1; }
osascript -e 'tell application "System Events"' -e 'keystroke "a" using command down' -e 'delay 0.1' -e 'key code 51' -e 'end tell' >/dev/null; sleep 0.4
