#!/usr/bin/env python3
"""Generatore statico di disdettaabbonamento.it.
Legge data/brands-*.json e scrive il sito in site/.
Uso : python3 _build/build.py
"""
import json, glob, os, html, re, shutil, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
DOMAIN = "https://disdettaabbonamento.it"
SITE = "Disdetta Abbonamento"
TODAY = dt.date.today().isoformat()
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def data_it(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MESI[int(m) - 1]} {y}"


E = lambda s: html.escape(str(s or ""), quote=True)

CATEGORIE = {
    "telefonia": {
        "nome": "Telefonia e internet", "slug": "telefonia",
        "intro": "Linea fissa, fibra, ADSL e SIM mobile. Per legge il preavviso non può superare i 30 giorni e l'operatore può addebitare solo i costi giustificati dalla chiusura del servizio.",
        "legge": "Ai sensi dell'art. 1, comma 3, del D.L. 7/2007, convertito dalla Legge 40/2007 (legge Bersani), il cliente può recedere in qualsiasi momento dai contratti con operatori di telefonia e comunicazione elettronica, con un preavviso non superiore a 30 giorni.",
        "servizio": "al servizio di telefonia e/o connettività",
    },
    "tv-streaming": {
        "nome": "TV e streaming", "slug": "tv-streaming",
        "intro": "Pay TV e piattaforme di streaming. Le piattaforme online si disdicono dall'account in pochi clic; per la pay TV con contratto serve spesso una comunicazione scritta.",
        "legge": "Per i contratti con operatori di reti televisive vale la Legge 40/2007: il recesso è possibile in qualsiasi momento con un preavviso massimo di 30 giorni.",
        "servizio": "all'abbonamento televisivo",
    },
    "energia": {
        "nome": "Luce e gas", "slug": "luce-gas",
        "intro": "Per cambiare fornitore non serve nessuna disdetta: se ne occupa il nuovo fornitore. La lettera serve solo per chiudere la fornitura, per esempio quando lasci una casa.",
        "legge": "Per cambiare fornitore di luce o gas non è necessario disdire il vecchio contratto: il recesso è gestito dal nuovo venditore. La disdetta scritta serve per la cessazione definitiva della fornitura.",
        "servizio": "alla fornitura di energia elettrica e/o gas naturale",
    },
    "assicurazioni": {
        "nome": "Assicurazioni", "slug": "assicurazioni",
        "intro": "L'RC auto non si rinnova più in automatico dal 2012, quindi non serve disdirla alla scadenza. Le altre polizze (casa, vita, infortuni) spesso sì, con un preavviso indicato nel contratto.",
        "legge": "Dal 2012 (D.L. 179/2012) le polizze RC auto non prevedono il tacito rinnovo. Per le altre polizze la disdetta va inviata entro il termine di preavviso indicato nelle condizioni di contratto, di solito 30 o 60 giorni prima della scadenza.",
        "servizio": "alla polizza assicurativa",
    },
    "palestre": {
        "nome": "Palestre", "slug": "palestre",
        "intro": "Gli abbonamenti in palestra hanno spesso una durata minima e un preavviso preciso prima della scadenza. Spesso il contratto è con il singolo club, non con il marchio.",
        "legge": "Il recesso dall'abbonamento è regolato dalle condizioni generali sottoscritte: durata minima, preavviso e modalità di invio. Conserva la ricevuta di invio come prova.",
        "servizio": "all'abbonamento",
    },
    "altri-servizi": {
        "nome": "Altri servizi", "slug": "altri-servizi",
        "intro": "Carte, pedaggi, allarmi, associazioni e altri abbonamenti, con le loro regole di disdetta.",
        "legge": "Le modalità di recesso sono quelle previste dalle condizioni generali del contratto. In mancanza di indicazioni, una raccomandata A/R o una PEC costituiscono prova dell'invio.",
        "servizio": "al servizio",
    },
}

CSS = """
:root{--fg:#14213d;--muted:#5c677d;--bg:#ffffff;--soft:#f4f7fb;--line:#dde3ec;--accent:#1d5fd1;--accent-d:#164aa6;--ok:#0f7b52;--okbg:#e3f6ee;--warn:#8a5a00;--warnbg:#fff4dd}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--fg);background:var(--bg)}
a{color:var(--accent)}a:hover{color:var(--accent-d)}
.wrap{max-width:860px;margin:0 auto;padding:0 18px}
header.top{border-bottom:1px solid var(--line);background:#fff}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:60px}
.logo{font-weight:800;font-size:19px;text-decoration:none;color:var(--fg)}.logo span{color:var(--accent)}
nav.main a{margin-left:16px;text-decoration:none;color:var(--muted);font-weight:600;font-size:15px}
h1{font-size:clamp(28px,5vw,40px);line-height:1.15;margin:28px 0 10px;letter-spacing:-.01em}
h2{font-size:24px;margin:38px 0 12px;line-height:1.25}h3{font-size:19px;margin:24px 0 8px}
.lead{font-size:19px;color:var(--muted);margin:0 0 18px}
.crumbs{font-size:14px;color:var(--muted);margin-top:18px}.crumbs a{color:var(--muted)}
.box{background:var(--soft);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0}
.facts{display:grid;grid-template-columns:180px 1fr;gap:8px 16px;margin:0}
.facts dt{font-weight:700;color:var(--muted);font-size:15px}.facts dd{margin:0;word-break:break-word}
.pec{font-family:ui-monospace,Menlo,monospace;font-size:15px;background:#fff;border:1px solid var(--line);border-radius:6px;padding:2px 6px}
.badge{display:inline-block;font-size:13px;font-weight:700;border-radius:999px;padding:3px 10px;background:var(--okbg);color:var(--ok)}
.note{background:var(--warnbg);border:1px solid #f1d9a6;color:#5b3d00;border-radius:12px;padding:14px 16px;margin:18px 0}
ul.canali li{margin:4px 0}
.gen{border:2px solid var(--accent);border-radius:16px;padding:20px;margin:22px 0;background:#fff}
.gen h2{margin-top:0}
.gen label{display:block;font-weight:600;font-size:15px;margin:12px 0 4px}
.gen input,.gen select{width:100%;font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}
.btn{display:inline-block;font:inherit;font-weight:700;border:0;border-radius:10px;padding:12px 18px;background:var(--accent);color:#fff;cursor:pointer;text-decoration:none;margin:14px 8px 0 0}
.btn.sec{background:#fff;color:var(--accent);border:2px solid var(--accent)}
.btn:hover{background:var(--accent-d);color:#fff}
#lettera{white-space:pre-wrap;font:15px/1.55 Georgia,serif;background:#fffef9;border:1px solid var(--line);border-radius:10px;padding:22px;margin-top:16px;display:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:14px 0}
.card{display:block;border:1px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--fg);background:#fff}
.card:hover{border-color:var(--accent)}.card b{display:block}.card small{color:var(--muted)}
details{border-bottom:1px solid var(--line);padding:12px 0}summary{font-weight:700;cursor:pointer}
.src{font-size:14px;color:var(--muted)}.src a{color:var(--muted)}
.search{width:100%;font:inherit;font-size:18px;padding:14px 16px;border:2px solid var(--line);border-radius:12px;margin:8px 0 4px}
footer{border-top:1px solid var(--line);margin-top:56px;padding:26px 0;color:var(--muted);font-size:14px;background:var(--soft)}
footer a{color:var(--muted);margin-right:14px}
@media(max-width:640px){.facts{grid-template-columns:1fr}.facts dt{margin-top:8px}.row2{grid-template-columns:1fr}nav.main{display:none}}
@media print{header.top,footer,.crumbs,.noprint,h1,.lead,.box,.note,h2,h3,ul,details,.grid,.src,p{display:none!important}.gen{border:0;padding:0}#lettera{display:block!important;border:0;background:#fff;font-size:12pt}}
"""

JS = r"""
function genLettera(){
  const f=document.getElementById('form-lettera'); const v=n=>(f.elements[n]&&f.elements[n].value||'').trim();
  const d=window.LETTERA; const oggi=new Date().toLocaleDateString('it-IT');
  const nome=v('nome')||'[Nome e cognome]', ind=v('indirizzo')||'[Indirizzo di residenza]', cf=v('cf');
  const cod=v('codice')||'[codice cliente / numero contratto]', linea=v('linea'), luogo=v('luogo')||'[Luogo]';
  let t='';
  t+=nome+'\n'+ind+(cf?'\nCodice fiscale: '+cf:'')+'\n\n';
  t+='Spett.le '+d.azienda+(d.postale?'\n'+d.postale:'')+(d.pec?'\nPEC: '+d.pec:'')+'\n\n';
  t+=(d.pec?'Inviata a mezzo PEC':'Raccomandata A/R')+'\n\n';
  t+='Oggetto: disdetta del contratto n. '+cod+(linea?' ('+d.campo+' '+linea+')':'')+'\n\n';
  t+='Il/La sottoscritto/a '+nome+', residente in '+ind+(cf?', codice fiscale '+cf:'')+', titolare del contratto n. '+cod+' relativo '+d.servizio+(linea?' ('+d.campo+' '+linea+')':'')+',\n\n';
  t+='COMUNICA\n\nla propria volontà di recedere dal suddetto contratto'+(d.legge?', '+d.legge:'')+', con effetto al termine del periodo di preavviso previsto.\n\n';
  t+='Chiede pertanto la cessazione del servizio e di ogni addebito successivo alla data di efficacia del recesso, con l\'interruzione di eventuali domiciliazioni bancarie o addebiti su carta collegati al contratto.'+(d.apparati?' Resta in attesa delle istruzioni per la restituzione degli apparati in comodato.':'')+'\n\n';
  t+='Si allega copia di un documento di identità in corso di validità.\n\nDistinti saluti.\n\n'+luogo+', '+oggi+'\n\nFirma\n\n____________________';
  const el=document.getElementById('lettera'); el.textContent=t; el.style.display='block';
  document.getElementById('azioni').style.display='block'; el.scrollIntoView({behavior:'smooth',block:'start'});
  return false;
}
function copiaLettera(b){navigator.clipboard.writeText(document.getElementById('lettera').textContent).then(()=>{b.textContent='Copiata';setTimeout(()=>b.textContent='Copia il testo',1500)})}
function filtra(q){q=q.toLowerCase().trim();document.querySelectorAll('[data-nome]').forEach(c=>{c.style.display=!q||c.dataset.nome.includes(q)?'':'none'})}
"""

LEGGE_BREVE = {
    "telefonia": "ai sensi dell'art. 1, comma 3, del D.L. 7/2007 convertito dalla Legge 40/2007",
    "tv-streaming": "ai sensi dell'art. 1, comma 3, del D.L. 7/2007 convertito dalla Legge 40/2007",
}
CAMPO = {"telefonia": "numero di linea", "tv-streaming": "codice cliente", "energia": "codice POD/PDR",
         "assicurazioni": "numero di polizza", "palestre": "numero di tessera", "altri-servizi": "riferimento"}


def page(title, desc, path, body, schema=None):
    canon = DOMAIN + path
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in (schema or []))
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canon}"><meta property="og:locale" content="it_IT">
<link rel="stylesheet" href="/style.css">{ld}</head><body>
<header class="top"><div class="wrap"><a class="logo" href="/">Disdetta<span>Abbonamento</span>.it</a>
<nav class="main"><a href="/telefonia/">Telefonia</a><a href="/luce-gas/">Luce e gas</a><a href="/assicurazioni/">Assicurazioni</a><a href="/come-funziona/">Come funziona</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap"><p><a href="/">Home</a><a href="/come-funziona/">Come funziona</a><a href="/chi-siamo/">Chi siamo</a><a href="/note-legali/">Note legali</a><a href="/privacy/">Privacy</a></p>
<p>{SITE} è un servizio indipendente, non affiliato agli operatori citati. I marchi appartengono ai rispettivi proprietari. Le informazioni sono verificate sulle fonti ufficiali alla data indicata in ogni pagina: controlla sempre il tuo contratto.</p></div></footer>
<script src="/app.js" defer></script></body></html>"""


def write(path, content):
    full = os.path.join(OUT, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)


def faq_brand(b, cat):
    n = b["nome"]; q = []
    if b.get("pec"):
        q.append((f"Qual è l'indirizzo PEC per la disdetta {n}?", f"L'indirizzo PEC indicato da {n} nei documenti ufficiali è {b['pec']}. Verificato il {data_it(b['data_verifica'])}."))
    if b.get("indirizzo_postale"):
        q.append((f"A quale indirizzo mandare la raccomandata per disdire {n}?", f"La raccomandata A/R va inviata a: {b['indirizzo_postale']}."))
    if b.get("preavviso"):
        q.append((f"Quanto preavviso serve per disdire {n}?", f"Preavviso: {b['preavviso']}. Il recesso diventa efficace alla fine di questo periodo."))
    if b.get("costi"):
        q.append((f"Disdire {n} costa qualcosa?", b["costi"]))
    if not b.get("pec") and not b.get("indirizzo_postale"):
        q.append((f"Serve una lettera per disdire {n}?", "No. La disdetta si fa direttamente dall'account o dai canali indicati sopra, senza inviare lettere."))
    return q


def brand_page(b, peers):
    cat = CATEGORIE[b["categoria"]]; n = b["nome"]; path = f"/disdetta-{b['slug']}/"
    lettera = bool(b.get("pec") or b.get("indirizzo_postale")) or b["categoria"] == "palestre"
    anno = TODAY[:4]
    title = f"Disdetta {n}: PEC, indirizzo e modulo ({anno})" if lettera else f"Disdetta {n}: come annullare l'abbonamento ({anno})"
    desc = (f"Come disdire {n}: indirizzo PEC, raccomandata, preavviso e costi verificati sulle fonti ufficiali. Genera gratis la lettera di disdetta pronta da inviare."
            if lettera else f"Come annullare l'abbonamento {n} in pochi passaggi, senza lettere. Preavviso, costi e cosa succede dopo, verificato sulle fonti ufficiali.")
    facts = []
    if b.get("pec"): facts.append(("PEC", f'<span class="pec">{E(b["pec"])}</span>'))
    if b.get("indirizzo_postale"): facts.append(("Raccomandata A/R", E(b["indirizzo_postale"])))
    if b.get("preavviso"): facts.append(("Preavviso", E(b["preavviso"])))
    if b.get("costi"): facts.append(("Costi", E(b["costi"])))
    if b.get("modulo"): facts.append(("Modulo ufficiale", f'<a href="{E(b["modulo"])}" rel="nofollow noopener" target="_blank">scarica il modulo di {E(n)}</a>'))
    facts.append(("Verificato il", f'{data_it(b["data_verifica"])} <span class="badge">{"fonte ufficiale" if b.get("affidabilita") == "ufficiale" else "fonte secondaria"}</span>'))
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
    canali = "".join(f"<li>{E(c)}</li>" for c in b.get("canali", []))
    body = f'<p class="crumbs"><a href="/">Home</a> › <a href="/{cat["slug"]}/">{E(cat["nome"])}</a> › {E(n)}</p>'
    body += f"<h1>Disdetta {E(n)}</h1>"
    body += (f'<p class="lead">Tutto quello che serve per disdire {E(n)}: dove inviare la richiesta, con quale preavviso e una lettera già pronta da compilare.</p>'
             if lettera else f'<p class="lead">{E(n)} si disdice online, senza lettere. Ecco come fare e cosa succede dopo.</p>')
    body += f'<div class="box"><dl class="facts">{dl}</dl></div>'
    if b.get("note"):
        body += f'<div class="note"><strong>Da sapere.</strong> {E(b["note"])}</div>'
    body += f"<h2>Come disdire {E(n)}: i canali</h2><ul class=\"canali\">{canali}</ul>"
    if lettera:
        via = "PEC" if b.get("pec") else "raccomandata A/R"
        body += f"""<section class="gen" id="lettera-disdetta"><h2>Lettera di disdetta {E(n)}, gratis</h2>
<p>Compila i campi, la lettera si genera qui sotto. Puoi copiarla o salvarla in PDF e inviarla via {via}. I dati restano sul tuo dispositivo, non vengono inviati a nessuno.</p>
<form id="form-lettera" onsubmit="return genLettera()">
<div class="row2"><div><label for="nome">Nome e cognome dell'intestatario</label><input id="nome" name="nome" autocomplete="name"></div>
<div><label for="cf">Codice fiscale (facoltativo)</label><input id="cf" name="cf"></div></div>
<label for="indirizzo">Indirizzo di residenza</label><input id="indirizzo" name="indirizzo" autocomplete="street-address">
<div class="row2"><div><label for="codice">Codice cliente o numero di contratto</label><input id="codice" name="codice"></div>
<div><label for="linea">{E(CAMPO[b["categoria"]].capitalize())} (facoltativo)</label><input id="linea" name="linea"></div></div>
<label for="luogo">Luogo</label><input id="luogo" name="luogo" autocomplete="address-level2">
<button class="btn" type="submit">Genera la lettera</button></form>
<div id="lettera"></div>
<div id="azioni" class="noprint" style="display:none"><button class="btn" type="button" onclick="copiaLettera(this)">Copia il testo</button><button class="btn sec" type="button" onclick="window.print()">Salva in PDF / stampa</button>
<p class="src">Per una disdetta con valore legale, invia la lettera firmata con copia del documento d'identità da una casella PEC, oppure con raccomandata A/R, e conserva la ricevuta.</p></div>
<script>window.LETTERA={json.dumps({"azienda": n, "pec": b.get("pec", ""), "postale": b.get("indirizzo_postale", "") or ("[indirizzo del tuo club, indicato nel contratto]" if b["categoria"] == "palestre" else ""), "servizio": cat["servizio"], "legge": LEGGE_BREVE.get(b["categoria"], ""), "campo": CAMPO[b["categoria"]], "apparati": b["categoria"] in ("telefonia", "tv-streaming")}, ensure_ascii=False)}</script>
</section>"""
    body += f"<h2>Cosa dice la legge</h2><p>{E(cat['legge'])}</p>"
    faqs = faq_brand(b, cat)
    if faqs:
        body += "<h2>Domande frequenti</h2>" + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    if peers:
        body += f"<h2>Altre disdette: {E(cat['nome'].lower())}</h2><div class=\"grid\">" + "".join(
            f'<a class="card" href="/disdetta-{p["slug"]}/"><b>Disdetta {E(p["nome"])}</b><small>{etichetta(p)}</small></a>' for p in peers) + "</div>"
    host = lambda u: re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
    fonti = " · ".join(f'<a href="{E(u)}" rel="nofollow noopener" target="_blank">{E(host(u))}</a>' for u in b.get("fonti", []))
    body += f'<p class="src">Fonti consultate il {data_it(b["data_verifica"])}: {fonti}. Le condizioni possono cambiare: in caso di dubbio fa fede il tuo contratto.</p>'
    schema = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}] if faqs else []
    schema.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": cat["nome"], "item": f"{DOMAIN}/{cat['slug']}/"},
        {"@type": "ListItem", "position": 3, "name": f"Disdetta {n}", "item": DOMAIN + path}]})
    write(path, page(title, desc, path, body, schema))
    return path


def etichetta(b):
    return "PEC e lettera pronta" if b.get("pec") else ("raccomandata e lettera pronta" if (b.get("indirizzo_postale") or b["categoria"] == "palestre") else "si disdice online")


def card(b):
    return (f'<a class="card" data-nome="{E(b["nome"].lower())}" href="/disdetta-{b["slug"]}/"><b>Disdetta {E(b["nome"])}</b>'
            f'<small>{etichetta(b)}</small></a>')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    brands = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "brands-*.json"))):
        try:
            brands += json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print("salto", f, e)
    brands = [b for b in brands if b.get("categoria") in CATEGORIE]
    urls = ["/"]
    bycat = {}
    for b in brands:
        bycat.setdefault(b["categoria"], []).append(b)
    for c, lst in bycat.items():
        lst.sort(key=lambda b: b["nome"].lower())
        for i, b in enumerate(lst):
            peers = [lst[(i + k) % len(lst)] for k in range(1, min(len(lst), 7))]
            urls.append(brand_page(b, peers))
        cat = CATEGORIE[c]; p = f"/{cat['slug']}/"
        body = f'<p class="crumbs"><a href="/">Home</a> › {E(cat["nome"])}</p><h1>Disdetta {E(cat["nome"].lower())}</h1><p class="lead">{E(cat["intro"])}</p>'
        body += '<div class="grid">' + "".join(card(b) for b in lst) + "</div>"
        body += f"<h2>Cosa dice la legge</h2><p>{E(cat['legge'])}</p>"
        write(p, page(f"Disdetta {cat['nome'].lower()}: PEC, indirizzi e moduli ({TODAY[:4]})",
                      f"Come disdire {cat['nome'].lower()}: indirizzi PEC e postali, preavviso e lettere di disdetta gratuite per {len(lst)} operatori, verificati sulle fonti ufficiali.", p, body))
        urls.append(p)
    # home
    body = '<h1>Disdetta abbonamento: indirizzi PEC e lettere pronte</h1><p class="lead">Cerca il tuo operatore: trovi l\'indirizzo PEC o postale giusto, il preavviso, i costi e una lettera di disdetta gratuita da compilare in un minuto.</p>'
    body += '<input class="search" type="search" placeholder="Cerca un operatore: TIM, Sky, Enel, McFit…" oninput="filtra(this.value)" aria-label="Cerca un operatore">'
    for c in CATEGORIE:
        if c in bycat:
            cat = CATEGORIE[c]
            body += f'<h2><a href="/{cat["slug"]}/">{E(cat["nome"])}</a></h2><div class="grid">' + "".join(card(b) for b in bycat[c]) + "</div>"
    body += '<h2>Come funziona</h2><p>Ogni scheda riporta gli indirizzi ufficiali dell\'operatore, verificati sui suoi documenti, con la data dell\'ultima verifica. Compili la lettera, la scarichi e la invii tu, via PEC o raccomandata. Il servizio è gratuito.</p>'
    write("/", page("Disdetta abbonamento: PEC, indirizzi e lettere di disdetta gratis",
                    f"Indirizzi PEC e postali verificati, preavviso, costi e lettere di disdetta gratuite per {len(brands)} operatori: telefonia, pay TV, luce e gas, assicurazioni, palestre.", "/", body,
                    [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": DOMAIN + "/"}]))
    # pagine istituzionali
    statiche = {
        "/come-funziona/": ("Come funziona", "Come disdire un contratto con valore legale: PEC o raccomandata A/R, documento d'identità, ricevuta da conservare.",
            "<h1>Come disdire un contratto, passo per passo</h1><ol><li><strong>Trova l'operatore</strong> e controlla preavviso e costi nella sua scheda.</li><li><strong>Compila la lettera</strong>: nome dell'intestatario, indirizzo, codice cliente o numero di contratto.</li><li><strong>Firma la lettera</strong> e allega una copia del documento d'identità.</li><li><strong>Inviala</strong> via PEC dalla tua casella PEC, oppure con raccomandata A/R all'indirizzo indicato.</li><li><strong>Conserva la ricevuta</strong> di consegna: è la prova della data della disdetta.</li></ol><h2>PEC o raccomandata?</h2><p>La PEC ha lo stesso valore legale della raccomandata con ricevuta di ritorno, costa meno ed è immediata. Alcuni operatori accettano solo PEC inviate da un'altra casella PEC, non da un'e-mail normale.</p>"),
        "/chi-siamo/": ("Chi siamo", "Disdetta Abbonamento è un servizio indipendente che raccoglie gli indirizzi ufficiali per disdire i contratti.",
            "<h1>Chi siamo</h1><p>Disdetta Abbonamento è un servizio indipendente, non collegato a nessun operatore. Raccogliamo dai documenti ufficiali degli operatori gli indirizzi PEC e postali, i preavvisi e i costi di disdetta, e li aggiorniamo con la data di verifica in ogni scheda.</p><p>Hai trovato un dato non aggiornato? Scrivici a <a href='mailto:info@disdettaabbonamento.it'>info@disdettaabbonamento.it</a>: verifichiamo e correggiamo.</p>"),
        "/note-legali/": ("Note legali", "Note legali di Disdetta Abbonamento.",
            "<h1>Note legali</h1><h2>Editore del sito</h2><p>Louis Lardeux, imprenditore individuale (micro-entreprise di diritto francese), SIREN 999 443 880, Francia. Contatto: <a href='mailto:info@disdettaabbonamento.it'>info@disdettaabbonamento.it</a>.</p><h2>Informazioni</h2><p>Le informazioni pubblicate hanno scopo informativo e sono verificate sulle fonti ufficiali alla data indicata in ogni scheda. Non costituiscono consulenza legale. In caso di dubbio fa fede il contratto sottoscritto con l'operatore.</p><p>I marchi citati appartengono ai rispettivi titolari e sono usati solo per identificare i servizi.</p>"),
        "/privacy/": ("Privacy", "Informativa privacy di Disdetta Abbonamento.",
            "<h1>Privacy</h1><p>Il generatore di lettere funziona interamente nel tuo browser: i dati che inserisci non vengono inviati né salvati sui nostri server.</p>"),
    }
    for p, (t, d, b) in statiche.items():
        write(p, page(f"{t} | {SITE}", d, p, b)); urls.append(p)
    open(os.path.join(OUT, "style.css"), "w").write(CSS)
    open(os.path.join(OUT, "app.js"), "w").write(JS)
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    sm = "".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    open(os.path.join(OUT, "CNAME"), "w").write("disdettaabbonamento.it\n")
    k = open(os.path.join(ROOT, "_build", "indexnow.key")).read().strip()
    open(os.path.join(OUT, k + ".txt"), "w").write(k)
    open(os.path.join(ROOT, "_build", "urls.txt"), "w").write("\n".join(DOMAIN + u for u in urls) + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print(f"{len(brands)} marchi, {len(urls)} pagine -> {OUT}")


if __name__ == "__main__":
    main()
