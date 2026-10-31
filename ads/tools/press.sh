#!/bin/zsh
# usage: press.sh '<regex du libellé exact>'  -> focus par script + touche Entrée
D=$(dirname $0); $D/sfront.sh >/dev/null; sleep 0.2
R=$($D/sjs.sh "(()=>{const b=[...document.querySelectorAll('material-button,button,a[role=button],a')].filter(e=>e.getBoundingClientRect().width>0).find(e=>/^$1\$/.test((e.innerText||'').trim()));if(!b)return 'NOBTN';b.scrollIntoView({block:'center'});const f=b.querySelector('[tabindex],button')||b;f.setAttribute('tabindex','0');f.focus();return 'focused'})()")
echo "$R"; [ "$R" = "focused" ] || exit 1
osascript -e 'tell application "System Events" to key code 36' >/dev/null
