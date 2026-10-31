#!/bin/zsh
# usage: grpfull.sh <index gruppi.json> — remplit mots clés, URL, chemins, 10 titres, 3 descriptions du groupe courant
D=$(dirname $0); J=~/Documents/disdetta-it/ads/gruppi.json
for pass in 1 2 3; do
LIST=$($D/sjs.sh '(()=>{return JSON.stringify([...document.querySelectorAll("input,textarea")].filter(e=>e.getBoundingClientRect().width>0).map(e=>(e.getAttribute("aria-label")||e.placeholder||"")+"|"+e.value))})()')
python3 - "$1" "$LIST" "$pass" <<'PY' > /tmp/grp_plan.txt
import json,sys,os
idx=int(sys.argv[1]); L=json.loads(sys.argv[2]); p=int(sys.argv[3]); g=json.load(open(os.path.expanduser('~/Documents/disdetta-it/ads/gruppi.json')))[idx]
lab=[x.split("|",1)[0].replace("\xa0"," ") for x in L]; val=[x.split("|",1)[1] for x in L]
def find(s): return next(i for i,l in enumerate(lab) if l.startswith(s))
kw=find("Saisissez ou collez"); url=find("URL finale"); p1=find("Chemin 1"); p2=find("Chemin 2")
descs=[i for i,l in enumerate(lab) if l=="Description"]
heads=[i for i in range(p2+1,descs[0]) if lab[i]==""]
plan=[]
if p==1: plan+=[(kw,", ".join('"'+k+'"' for k in g["keywords"])),(url,g["url"]),(p1,g["path1"]),(p2,"pec")]
placed=[val[i] for i in heads if val[i]]
todo=[h for h in g["headlines"] if h not in placed]
empty=[i for i in heads if not val[i]]
for i,h in zip(empty,todo): plan.append((i,h))
dplaced=[val[i] for i in descs if val[i]]
dtodo=[d for d in g["descriptions"] if d not in dplaced]
dempty=[i for i in descs if not val[i]] if p==1 else [i for i in descs if not val[i]]
if p==1:
    # écraser les descriptions préremplies éventuelles
    for i,d in zip(descs,g["descriptions"]): plan.append((i,d))
else:
    for i,d in zip(dempty,dtodo): plan.append((i,d))
print(f"pass {p}: headslots={len(heads)} empty={len(empty)} todo={len(todo)}",file=sys.stderr)
for i,v in plan: print(f"{i}\t{v}")
PY
[ -s /tmp/grp_plan.txt ] || break
while IFS=$'\t' read -r i v; do $D/fill2.sh "$i" "$v" || echo "fail $i"; done < /tmp/grp_plan.txt
sleep 1
done
$D/sjs.sh '(()=>{const t=document.body.innerText.replace(/\s+/g," ");const L=[...document.querySelectorAll("input,textarea")].filter(e=>e.getBoundingClientRect().width>0);return "titres="+L.filter(e=>!e.getAttribute("aria-label")&&e.value&&e.value.length<=30&&!/^http/.test(e.value)).length+" troplong:"+(t.match(/Valeur trop longue/g)||[]).length+" eff:"+t.slice(t.indexOf("Efficacité de l")+30,t.indexOf("Efficacité de l")+48)})()'
