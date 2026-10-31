#!/bin/zsh
D=$(dirname $0)
$D/sfront.sh >/dev/null
sleep 0.5
JS="(()=>{const el=($1); if(!el) return 'NOEL'; el.scrollIntoView({block:'center'}); const r=el.getBoundingClientRect(); return JSON.stringify({x:window.screenX+r.left+r.width/2, y:window.screenY+(window.outerHeight-window.innerHeight)+r.top+r.height/2, w:r.width,h:r.height});})()"
R=$($D/sjs.sh "$JS")
case "$R" in NOEL|NOTAB) echo $R; exit 1;; esac
X=$(echo "$R" | python3 -c "import sys,json;d=json.load(sys.stdin);print(int(round(d['x'])))")
Y=$(echo "$R" | python3 -c "import sys,json;d=json.load(sys.stdin);print(int(round(d['y'])))")
osascript -e "tell application \"System Events\" to click at {$X, $Y}" >/dev/null
echo "clicked $X,$Y"
