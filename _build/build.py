#!/usr/bin/env python3
"""Generatore statico di disdettaabbonamento.it.
Legge data/brands-*.json e scrive il sito in site/.
Uso : python3 _build/build.py
"""
import json, glob, os, html, re, shutil, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guide import GUIDE

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
:root{--fg:#0f1b33;--muted:#58647a;--bg:#fff;--soft:#f3f6fb;--line:#e1e6ef;--accent:#1f5eff;--accent-d:#1748c9;--accent-l:#e8efff;--ok:#0b7a4f;--okbg:#dff5ea;--warnbg:#fff6e0;--radius:16px;--shadow:0 10px 30px rgba(15,27,51,.08),0 2px 6px rgba(15,27,51,.05)}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--fg);background:var(--bg);overflow-x:hidden}
a{color:var(--accent)}a:hover{color:var(--accent-d)}
.wrap,main{max-width:1040px;margin:0 auto;padding:0 18px}
header.top{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.92);backdrop-filter:saturate(1.4) blur(8px);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:9px;font-weight:800;font-size:19px;text-decoration:none;color:var(--fg)}.logo .lt span{color:var(--accent)}
.logo i{width:30px;height:30px;border-radius:9px;background:linear-gradient(135deg,#1f5eff,#00b4d8);display:grid;place-items:center;color:#fff;font-style:normal;font-size:16px}
nav.main{display:flex;align-items:center;gap:18px}nav.main a{text-decoration:none;color:var(--muted);font-weight:600;font-size:15px}
nav.main a.cta{color:#fff;background:var(--accent);padding:9px 16px;border-radius:999px}nav.main a.cta:hover{background:var(--accent-d)}nav.main .sm{display:none}
.hero{margin:0 calc(50% - 50vw);padding:48px calc(50vw - 50% + 18px) 40px;background:radial-gradient(1200px 400px at 80% -10%,#dbe6ff 0,transparent 60%),radial-gradient(800px 300px at 0% 0%,#e3fbff 0,transparent 55%),var(--soft);border-bottom:1px solid var(--line)}
.hero.small{padding-top:28px;padding-bottom:30px}
.pill{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-size:14px;font-weight:600;color:var(--muted)}
.pill b{color:var(--ok)}
h1{font-size:clamp(30px,5.2vw,50px);line-height:1.1;margin:16px 0 12px;letter-spacing:-.02em}
h1 em{font-style:normal;background:linear-gradient(90deg,#1f5eff,#00a3c4);-webkit-background-clip:text;background-clip:text;color:transparent}
h2{font-size:clamp(23px,3vw,30px);margin:46px 0 14px;line-height:1.2;letter-spacing:-.01em}h3{font-size:19px;margin:0 0 6px}
.lead{font-size:clamp(17px,2.2vw,20px);color:var(--muted);margin:0 0 20px;max-width:720px}
.crumbs{font-size:14px;color:var(--muted)}.crumbs a{color:var(--muted)}
.searchbox{position:relative;max-width:640px}
.search{width:100%;font:inherit;font-size:18px;padding:17px 18px 17px 50px;border:2px solid transparent;border-radius:14px;background:#fff;box-shadow:var(--shadow)}
.search:focus{outline:none;border-color:var(--accent)}
.searchbox:before{content:"";position:absolute;left:18px;top:50%;width:18px;height:18px;transform:translateY(-50%);background:no-repeat center/contain url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2358647a' stroke-width='2.4'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m20 20-4-4'/%3E%3C/svg%3E")}
.chips{display:flex;flex-wrap:wrap;gap:10px 18px;margin:18px 0 0;padding:0;list-style:none;font-size:15px;color:var(--muted);font-weight:600}
.chips li:before{content:"✓";display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:var(--okbg);color:var(--ok);font-size:12px;margin-right:7px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:28px;max-width:760px}
.stats div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.stats b{display:block;font-size:26px;line-height:1.1}.stats span{font-size:14px;color:var(--muted)}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-weight:700;border:0;border-radius:12px;padding:14px 22px;background:var(--accent);color:#fff;cursor:pointer;text-decoration:none;margin:8px 10px 0 0;box-shadow:0 6px 16px rgba(31,94,255,.25);transition:transform .15s,background .15s}
.btn:hover{background:var(--accent-d);color:#fff;transform:translateY(-1px)}
.btn.sec{background:#fff;color:var(--accent);border:2px solid var(--accent);box-shadow:none}.btn.sec:hover{background:var(--accent-l);color:var(--accent)}
.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:16px 0}
.step{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow)}
.step .n{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;font-weight:800;color:#fff;background:linear-gradient(135deg,#1f5eff,#00b4d8);margin-bottom:12px}
.step p{margin:0;color:var(--muted);font-size:15.5px}
.box{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:22px 24px;margin:22px 0;box-shadow:var(--shadow)}
.box h2{margin-top:0;font-size:22px}
.facts{display:grid;grid-template-columns:190px minmax(0,1fr);gap:12px 18px;margin:0}
.facts dt{font-weight:700;color:var(--muted);font-size:15px}.facts dd{margin:0;word-break:break-word}
.pec{display:inline-flex;align-items:center;gap:8px;font-family:ui-monospace,Menlo,monospace;font-size:15px;background:var(--accent-l);border-radius:8px;padding:4px 10px;color:var(--accent-d);font-weight:600}
.copy{font:inherit;font-size:13px;font-weight:700;border:1px solid var(--line);background:#fff;border-radius:8px;padding:3px 9px;cursor:pointer;color:var(--muted)}
.badge{display:inline-block;font-size:13px;font-weight:700;border-radius:999px;padding:3px 10px;background:var(--okbg);color:var(--ok)}
.note{background:var(--warnbg);border:1px solid #f3dca5;color:#5b3d00;border-radius:14px;padding:16px 18px;margin:20px 0}
ul.canali{padding:0;list-style:none;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
ul.canali li{background:var(--soft);border-radius:12px;padding:10px 14px;font-size:15.5px}
.gen{border:0;border-radius:20px;padding:26px;margin:28px 0;background:linear-gradient(180deg,#f0f5ff,#fff 60%);box-shadow:0 0 0 2px var(--accent) inset,var(--shadow);scroll-margin-top:84px}
.gen h2{margin-top:0}.gen .sub{color:var(--muted);margin-top:-6px}
.gen label{display:block;font-weight:600;font-size:15px;margin:14px 0 5px}
.gen input{width:100%;font:inherit;padding:12px 14px;border:1px solid var(--line);border-radius:11px;background:#fff}
.gen input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-l)}
.row2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0 14px}
.secure{font-size:14px;color:var(--ok);font-weight:600;margin-top:12px}
#lettera{white-space:pre-wrap;font:15px/1.6 Georgia,serif;background:#fff;border:1px solid var(--line);border-radius:12px;padding:26px;margin-top:18px;display:none;box-shadow:var(--shadow)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:14px 0}
.card{display:flex;align-items:center;gap:12px;border:1px solid var(--line);border-radius:14px;padding:13px 15px;text-decoration:none;color:var(--fg);background:#fff;transition:border-color .15s,transform .15s,box-shadow .15s}
.card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:var(--shadow);color:var(--fg)}
.card .av{flex:none;width:40px;height:40px;border-radius:11px;display:grid;place-items:center;font-weight:800;color:#fff;font-size:15px}
.card b{display:block;line-height:1.25}.card small{color:var(--muted);font-size:13.5px}
.av.telefonia{background:#1f5eff}.av.tv-streaming{background:#7b3fe4}.av.energia{background:#f08c00}.av.assicurazioni{background:#0b7a4f}.av.palestre{background:#e5484d}.av.altri-servizi{background:#475569}
.cats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.cat{display:block;text-decoration:none;color:var(--fg);background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow);transition:transform .15s}
.cat:hover{transform:translateY(-2px);color:var(--fg)}.cat .ic{font-size:26px}.cat small{color:var(--muted)}
.trust{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.trust div{background:var(--soft);border-radius:var(--radius);padding:20px}.trust p{margin:0;color:var(--muted);font-size:15.5px}
.band{margin:56px calc(50% - 50vw) 0;padding:44px calc(50vw - 50% + 18px);background:linear-gradient(120deg,#1f5eff,#0a8fc7);color:#fff;text-align:center}
.band h2{margin:0 0 8px;color:#fff}.band p{margin:0 0 18px;opacity:.9}.band .btn{background:#fff;color:var(--accent-d);box-shadow:none}
.searchbox{z-index:5}.suggest{display:none;position:absolute;left:0;right:0;top:calc(100% + 8px);background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 20px 50px rgba(15,27,51,.18);padding:6px;max-height:420px;overflow:auto;z-index:40}
.suggest a{display:flex;align-items:center;gap:12px;padding:9px 10px;border-radius:10px;text-decoration:none;color:var(--fg)}.suggest a:hover,.suggest a.on{background:var(--accent-l)}
.suggest b{display:block;line-height:1.2}.suggest small{color:var(--muted);font-size:13px}.suggest .av{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;color:#fff;font-weight:800;font-size:13px;flex:none}
.suggest .none{padding:12px;color:var(--muted);font-size:15px}
.plans{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin:22px 0 4px}
.plan{position:relative;background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px}
.plan.pro{border:2px solid var(--accent);box-shadow:0 14px 40px rgba(31,94,255,.16)}
.plan .tag{position:absolute;top:-12px;left:20px;background:var(--accent);color:#fff;font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;border-radius:999px;padding:4px 10px}
.plan .price{font-size:30px;font-weight:800;margin:4px 0 10px}.plan .price small{font-size:15px;color:var(--muted);font-weight:600}
.plan ul{list-style:none;padding:0;margin:0 0 14px;font-size:15.5px}.plan li{padding:5px 0 5px 26px;position:relative}.plan li:before{content:"✓";position:absolute;left:0;color:var(--ok);font-weight:800}
.plan .btn{width:100%;justify-content:center;margin:0}.plan .soon{display:block;text-align:center;font-size:13.5px;color:var(--muted);margin-top:8px}
.guar{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}
.guar div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;font-size:14.5px;color:var(--muted)}.guar b{display:block;color:var(--fg);font-size:15.5px;margin-bottom:2px}
@media(max-width:820px){.plans{grid-template-columns:1fr}.guar{grid-template-columns:repeat(2,minmax(0,1fr))}}
.hero.home{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:34px;align-items:center}
.demo{position:relative;background:#fff;border-radius:18px;box-shadow:0 30px 70px rgba(15,27,51,.18);padding:22px 22px 26px;font:13.5px/1.55 Georgia,serif;color:#24324d;min-height:330px;transform:rotate(1.5deg)}
.demo .head{display:flex;gap:6px;margin-bottom:12px}.demo .head i{width:10px;height:10px;border-radius:50%;background:#e1e6ef}
.demo pre{white-space:pre-wrap;margin:0;font:inherit;min-height:250px}
.demo .caret{display:inline-block;width:2px;height:15px;background:var(--accent);vertical-align:-2px;animation:blink 1s steps(1) infinite}
.stamp{position:absolute;right:18px;bottom:18px;border:3px solid var(--ok);color:var(--ok);font:800 15px/1 system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;padding:8px 12px;border-radius:10px;transform:rotate(-8deg) scale(1.6);opacity:0;transition:transform .35s cubic-bezier(.2,1.4,.4,1),opacity .2s;background:#fff}
.stamp.on{opacity:1;transform:rotate(-8deg) scale(1)}
.float{position:absolute;z-index:2;background:#fff;border-radius:12px;box-shadow:var(--shadow);padding:8px 12px;font:600 13px system-ui,sans-serif;color:var(--fg);display:flex;gap:8px;align-items:center;animation:bob 5s ease-in-out infinite}
.float.f1{left:-30px;bottom:96px}.float.f2{right:-18px;top:-16px;animation-delay:-2.5s}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes blink{50%{opacity:0}}
.marquee{overflow:hidden;margin:0 calc(50% - 50vw);border-bottom:1px solid var(--line);background:#fff;padding:14px 0;-webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
.marquee .track{display:flex;gap:34px;width:max-content;animation:scroll 70s linear infinite}
.marquee span{font-weight:700;color:var(--muted);white-space:nowrap;font-size:15px}.marquee span b{color:var(--fg)}
@keyframes scroll{to{transform:translateX(-50%)}}
.rv{opacity:0;transform:translateY(18px);transition:opacity .6s ease,transform .6s ease}.rv.in{opacity:1;transform:none}
.urg{display:flex;gap:16px;align-items:center;background:linear-gradient(120deg,#fff4e5,#ffe9e2);border:1px solid #ffd2b8;border-radius:16px;padding:18px 20px;margin:22px 0}
.urg .ic{font-size:30px;animation:bob 3s ease-in-out infinite}.urg b{font-size:18px;display:block}.urg p{margin:4px 0 0;color:#6b3b12;font-size:15.5px}
.urg .btn{margin:0 0 0 auto;flex:none}
.reviews{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.rev{background:#fff;border:1px dashed #c9d3e3;border-radius:16px;padding:20px;color:var(--muted);font-size:15px}
.rev .st{color:#f5a623;letter-spacing:2px;font-size:18px}
.btn.shine{position:relative;overflow:hidden}.btn.shine:after{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.35) 50%,transparent 70%);transform:translateX(-120%);animation:shine 3.5s ease-in-out infinite}
@keyframes shine{60%,100%{transform:translateX(120%)}}
@media(max-width:820px){.hero.home{grid-template-columns:1fr}.demo{transform:none;margin-top:8px}.float.f1{left:8px;top:-14px}.float.f2{display:none}.reviews{grid-template-columns:1fr}.urg{flex-wrap:wrap}.urg .btn{margin:6px 0 0;width:100%;justify-content:center}}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}.rv{opacity:1;transform:none}}
article.guide{max-width:760px}article.guide ul,article.guide ol{padding-left:22px}article.guide li{margin:6px 0}
details{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin:10px 0}summary{font-weight:700;cursor:pointer}details p{margin:10px 0 0;color:var(--muted)}
.src{font-size:14px;color:var(--muted)}.src a{color:var(--muted)}
.why{display:flex;gap:14px;align-items:flex-start;background:var(--okbg);border-radius:14px;padding:16px 18px;margin:22px 0;color:#0d4f35;font-size:15.5px}.why b{display:block}
.sticky{position:fixed;left:0;right:0;bottom:0;z-index:30;padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:rgba(255,255,255,.96);border-top:1px solid var(--line);display:none}
.sticky .btn{width:100%;justify-content:center;margin:0}
footer{border-top:1px solid var(--line);margin-top:64px;padding:32px 0;color:var(--muted);font-size:14px;background:var(--soft)}
footer a{color:var(--muted);margin-right:16px}
@media(max-width:820px){nav.main a:not(.cta){display:none}.steps,.trust,.cats{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:640px){nav.main .lg{display:none}nav.main .sm{display:inline}.logo{font-size:16px}.logo i{width:26px;height:26px}.facts{grid-template-columns:1fr;gap:4px}.facts dt{margin-top:10px}.row2,ul.canali{grid-template-columns:1fr}.sticky{display:block}body.has-sticky footer{padding-bottom:90px}.hero{padding-top:30px}.gen{padding:18px}}
@media print{header.top,footer,.crumbs,.noprint,.hero,.box,.note,h2,h3,ul,details,.grid,.src,p,.steps,.why,.sticky{display:none!important}.gen{box-shadow:none;padding:0;background:#fff}#lettera{display:block!important;border:0;box-shadow:none;font-size:12pt}}
"""

JS = r"""
const LEGGI={
 'telefonia':{rif:"ai sensi dell'art. 1, comma 3, del D.L. 31 gennaio 2007, n. 7, convertito con modificazioni dalla Legge 2 aprile 2007, n. 40",extra:"senza l'applicazione di penali o di costi diversi da quelli giustificati da costi effettivamente sostenuti dall'operatore, come previsto dalla medesima norma;",app:"le istruzioni per la restituzione di eventuali apparati concessi in comodato d'uso;"},
 'tv-streaming':{rif:"ai sensi dell'art. 1, comma 3, del D.L. 31 gennaio 2007, n. 7, convertito con modificazioni dalla Legge 2 aprile 2007, n. 40",extra:"senza l'applicazione di penali o di costi diversi da quelli giustificati da costi effettivamente sostenuti dall'operatore;",app:"le istruzioni per la restituzione di decoder, smart card o altri apparati in comodato d'uso;"},
 'energia':{rif:"secondo quanto previsto dalle condizioni generali di fornitura e dalla regolazione ARERA",extra:"con la disattivazione del punto di fornitura e l'emissione della fattura di chiusura sulla base della lettura finale del contatore."},
 'assicurazioni':{rif:"alla sua naturale scadenza, ai sensi dell'art. 1899 del Codice Civile e delle condizioni di polizza, chiedendo che la stessa non venga rinnovata né prorogata",extra:"Chiede altresì il rimborso dell'eventuale quota di premio pagata e non goduta, ove prevista dalle condizioni di polizza."},
 'palestre':{rif:"nel rispetto dei termini di preavviso previsti dalle condizioni generali sottoscritte",extra:"Chiede che non venga effettuato alcun rinnovo automatico dell'abbonamento."},
 'altri-servizi':{rif:"nel rispetto delle condizioni generali del contratto",extra:""}
};
function genLettera(){
  const f=document.getElementById('form-lettera'); const v=n=>(f.elements[n]&&f.elements[n].value||'').trim();
  const d=window.LETTERA; const L=LEGGI[d.cat]||LEGGI['altri-servizi'];
  const oggi=new Date().toLocaleDateString('it-IT',{day:'numeric',month:'long',year:'numeric'});
  const nome=v('nome')||'[Nome e cognome]', ind=v('indirizzo')||'[Indirizzo di residenza]', cf=v('cf'), mail=v('email');
  const cod=v('codice')||'[codice cliente / numero di contratto]', linea=v('linea'), luogo=v('luogo')||'[Luogo]';
  const rifC='n. '+cod+(linea?' ('+d.campo+' '+linea+')':'');
  let t='';
  t+=nome+'\n'+ind+(cf?'\nC.F. '+cf:'')+(mail?'\n'+mail:'')+'\n\n';
  t+='Spett.le '+d.azienda+(d.postale?'\n'+d.postale:'')+(d.pec?'\nPEC: '+d.pec:'')+'\n\n';
  t+=luogo+', '+oggi+'\n\n'+(d.pec?'Trasmessa a mezzo posta elettronica certificata (PEC)':'Raccomandata con avviso di ricevimento')+'\n\n';
  t+='OGGETTO: '+(d.cat==='assicurazioni'?'disdetta della polizza ':d.cat==='energia'?'richiesta di cessazione della fornitura - contratto ':'recesso dal contratto ')+rifC+'\n\n';
  t+='Il/La sottoscritto/a '+nome+(cf?', codice fiscale '+cf:'')+', residente in '+ind+', in qualità di intestatario/a del contratto '+rifC+' relativo '+d.servizio+',\n\n';
  t+='COMUNICA\n\n';
  t+=(d.cat==='assicurazioni'?'la propria disdetta della suddetta polizza '+L.rif+'.':'la propria volontà di recedere dal suddetto contratto, '+L.rif+', con effetto dalla scadenza del termine di preavviso previsto'+(d.cat==='telefonia'||d.cat==='tv-streaming'?', che non può essere superiore a trenta giorni':'')+'.')+'\n\n';
  t+='CHIEDE\n\n';
  const ext=(d.cat==='telefonia'||d.cat==='tv-streaming'||d.cat==='energia')?L.extra:'';
  t+='- la cessazione '+(d.cat==='assicurazioni'?'della copertura alla scadenza':d.cat==='energia'?'della fornitura':'del servizio')+(ext?' '+ext:';')+'\n';
  if(L.app){t+='- '+L.app+'\n';}
  t+='- l\'interruzione di ogni addebito successivo alla data di efficacia del recesso, comprese eventuali domiciliazioni bancarie o addebiti su carta di credito collegati al contratto;\n';
  if(d.cat==='assicurazioni'||d.cat==='palestre'){t+='- '+L.extra.charAt(0).toLowerCase()+L.extra.slice(1).replace(/\.$/,';')+'\n';}
  t+='- conferma scritta della ricezione della presente e della data di cessazione del contratto'+(mail?', all\'indirizzo '+mail:'')+'.\n\n';
  t+='I dati personali contenuti nella presente sono comunicati al solo fine di dare esecuzione al recesso, ai sensi del Regolamento (UE) 2016/679.\n\n';
  t+='Si allega copia di un documento di identità in corso di validità.\n\nDistinti saluti.\n\n'+nome+'\n\n____________________\n(firma)';
  const el=document.getElementById('lettera'); el.textContent=t; el.style.display='block';
  document.getElementById('azioni').style.display='block'; el.scrollIntoView({behavior:'smooth',block:'start'});
  return false;
}
function copiaLettera(b){navigator.clipboard.writeText(document.getElementById('lettera').textContent).then(()=>{b.textContent='Copiata ✓';setTimeout(()=>b.textContent='Copia il testo',1500)})}
function copiaPec(b,v){navigator.clipboard.writeText(v).then(()=>{b.textContent='Copiato ✓';setTimeout(()=>b.textContent='Copia',1500)})}
const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
let OPS=null;
async function ops(){if(!OPS){OPS=await (await fetch('/operatori.json')).json();OPS.forEach(o=>o.k=norm(o.n+' '+o.c))}return OPS}
function initSearch(inp){
  const box=document.createElement('div'); box.className='suggest'; box.setAttribute('role','listbox'); inp.parentNode.appendChild(box);
  let items=[],sel=-1;
  const render=()=>{box.innerHTML=items.length?items.map((o,i)=>`<a href="${o.u}" role="option" class="${i===sel?'on':''}"><span class="av ${o.cc}">${o.i}</span><span><b>${o.n}</b><small>${o.c} · ${o.l}</small></span></a>`).join(''):(inp.value.trim()?'<div class="none">Nessun operatore trovato. <a href="/come-funziona/">Come disdire comunque</a></div>':'');box.style.display=box.innerHTML?'block':'none'};
  inp.addEventListener('input',async()=>{const q=norm(inp.value);const all=await ops();sel=-1;
    if(!q){items=[];return render()}
    const st=all.filter(o=>norm(o.n).startsWith(q)), inc=all.filter(o=>!norm(o.n).startsWith(q)&&o.k.includes(q));
    items=st.concat(inc).slice(0,8);render()});
  inp.addEventListener('keydown',e=>{if(!items.length)return;
    if(e.key==='ArrowDown'){sel=(sel+1)%items.length;render();e.preventDefault()}
    else if(e.key==='ArrowUp'){sel=(sel-1+items.length)%items.length;render();e.preventDefault()}
    else if(e.key==='Enter'){location.href=items[Math.max(sel,0)].u;e.preventDefault()}
    else if(e.key==='Escape'){items=[];render()}});
  inp.addEventListener('focus',()=>{ops();if(items.length)render()});
  document.addEventListener('click',e=>{if(!inp.parentNode.contains(e.target))box.style.display='none'});
}
document.querySelectorAll('input.search').forEach(initSearch);
(function(){const els=document.querySelectorAll('.rv');if(!('IntersectionObserver' in window)){els.forEach(e=>e.classList.add('in'));return}
 const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px'});els.forEach(e=>io.observe(e));
 setTimeout(()=>els.forEach(e=>e.classList.add('in')),3500)})();
document.querySelectorAll('[data-count]').forEach(el=>{const end=+el.dataset.count,suf=el.dataset.suf||'';let s=null;const step=ts=>{s=s||ts;const p=Math.min((ts-s)/1200,1);el.textContent=Math.round(end*(1-Math.pow(1-p,3)))+suf;if(p<1)requestAnimationFrame(step)};requestAnimationFrame(step)});
(function(){const pre=document.getElementById('demo-txt');if(!pre)return;const full=pre.dataset.t;const st=document.getElementById('stamp');let i=0;pre.textContent='';
 const caret=document.createElement('span');caret.className='caret';
 const tick=()=>{if(i<=full.length){pre.textContent=full.slice(0,i);pre.appendChild(caret);i+=Math.random()<.2?3:2;setTimeout(tick,22)}else{st.classList.add('on');setTimeout(()=>{st.classList.remove('on');i=0;tick()},4500)}};
 if(matchMedia('(prefers-reduced-motion: reduce)').matches){pre.textContent=full;st.classList.add('on')}else setTimeout(tick,600)})();
(function(){const el=document.getElementById('scad');if(!el)return;const g=+el.dataset.giorni;const d=new Date();d.setDate(d.getDate()+g);
 el.textContent=d.toLocaleDateString('it-IT',{weekday:'long',day:'numeric',month:'long'});
 const d2=new Date();d2.setDate(d2.getDate()+g+7);const e2=document.getElementById('scad2');if(e2)e2.textContent=d2.toLocaleDateString('it-IT',{day:'numeric',month:'long'})})();
"""

LEGGE_BREVE = {
    "telefonia": "ai sensi dell'art. 1, comma 3, del D.L. 7/2007 convertito dalla Legge 40/2007",
    "tv-streaming": "ai sensi dell'art. 1, comma 3, del D.L. 7/2007 convertito dalla Legge 40/2007",
}
CAMPO = {"telefonia": "numero di linea", "tv-streaming": "numero smart card o tessera", "energia": "codice POD/PDR",
         "assicurazioni": "numero di polizza", "palestre": "numero di tessera", "altri-servizi": "riferimento"}


PLANS = """<h2 id="invio">Come vuoi inviare la disdetta?</h2>
<div class="rv plans">
<div class="plan"><h3>Fai da te</h3><div class="price">Gratis</div><ul><li>Lettera pronta, scritta secondo la normativa</li><li>La copi o la salvi in PDF</li><li>La invii tu dalla tua casella PEC o con raccomandata in posta</li></ul><a class="btn sec" href="#lettera-disdetta">Genera la lettera gratis</a></div>
<div class="plan pro"><span class="tag">Consigliato</span><h3>Te la inviamo noi via PEC</h3><div class="price">7,90 € <small>una tantum</small></div><ul><li>Lettera redatta secondo la legge, con i riferimenti normativi corretti</li><li>Inviata in PEC all'indirizzo verificato dell'operatore</li><li>Ricevuta di consegna con valore legale, inviata alla tua e-mail</li><li>Non serve avere una PEC né andare in posta</li><li>Rimborso completo se la PEC non viene consegnata</li></ul><a class="btn" href="mailto:info@disdettaabbonamento.it?subject=Invio%20disdetta%20via%20PEC">Invia via PEC, 7,90 €</a><span class="soon">Pagamento sicuro online in arrivo: per ora scrivici e ti rispondiamo in giornata. <a href="/termini/">Termini del servizio</a></span></div>
</div>
<div class="rv guar"><div><b>⚖️ Conforme alla legge</b>Testo con le norme del settore: legge Bersani, Codice civile, regole ARERA.</div><div><b>📬 Prova legale</b>La ricevuta PEC ha lo stesso valore di una raccomandata A/R.</div><div><b>🔎 Indirizzi verificati</b>Presi dai documenti ufficiali, con data di verifica.</div><div><b>🔒 Dati protetti</b>Nessun dato salvato per la lettera gratuita, GDPR per l'invio.</div></div>"""


DEMO_TXT = ("Spett.le Sky Italia\nPEC: servizioclientisky@pec.skytv.it\n\nOGGETTO: recesso dal contratto n. 12345678\n\n"
            "Il sottoscritto Mario Rossi, intestatario del contratto,\n\nCOMUNICA\n\nla propria volontà di recedere dal suddetto contratto, "
            "ai sensi dell'art. 1, comma 3, della Legge 40/2007, con effetto dalla scadenza del preavviso.\n\n"
            "CHIEDE la cessazione di ogni addebito e conferma scritta.\n\nDistinti saluti.")


def demo_html(brands):
    d = ('<div class="demo" aria-hidden="true"><div class="float f1">⚡ Lettera pronta in 1 minuto</div><div class="float f2">🔒 Nessun dato salvato</div>'
         '<div class="head"><i></i><i></i><i></i></div><pre id="demo-txt" data-t="' + E(DEMO_TXT) + '"></pre><div class="stamp" id="stamp">PEC consegnata ✓</div></div></section>')
    m = '<div class="marquee" aria-hidden="true"><div class="track">' + "".join(f'<span>✓ <b>{E(b["nome"])}</b></span>' for b in brands * 2) + '</div></div>'
    return d + m


REVIEWS = ('<h2>Le recensioni</h2><div class="reviews rv"><div class="rev"><div class="st">★★★★★</div><p>Il servizio è appena nato: qui pubblicheremo solo recensioni vere dei primi utenti.</p></div>'
           '<div class="rev"><div class="st">★★★★★</div><p>Hai usato una lettera o l\'invio PEC? Raccontaci com\'è andata a <a href="mailto:info@disdettaabbonamento.it">info@disdettaabbonamento.it</a>.</p></div>'
           '<div class="rev"><div class="st">★★★★★</div><p>Ogni recensione viene pubblicata con nome e data, senza filtri.</p></div></div>')


TERMINI_HTML = r'''<h1>Termini e condizioni del servizio</h1>
<p class="src">Versione del 26 ottobre 2026.</p>
<h2>1. Chi siamo</h2>
<p>Il servizio è fornito da Louis Lardeux, imprenditore individuale (micro-entreprise di diritto francese), SIREN 999 443 880, Francia (di seguito «noi»). Contatto: <a href="mailto:info@disdettaabbonamento.it">info@disdettaabbonamento.it</a>.</p>
<h2>2. I servizi</h2>
<p><strong>Generatore di lettere, gratuito.</strong> Il sito mette a disposizione schede informative sugli operatori e un generatore di lettere di disdetta che funziona nel browser dell'utente. L'utente invia la lettera in autonomia.</p>
<p><strong>Invio via PEC per conto del cliente, a pagamento.</strong> Su richiesta del cliente inviamo la sua lettera di disdetta, firmata dal cliente o redatta a suo nome, all'indirizzo PEC dell'operatore indicato nella scheda, e gli trasmettiamo per e-mail le ricevute di accettazione e di consegna rilasciate dal sistema PEC.</p>
<h2>3. Mandato</h2>
<p>Ordinando l'invio, il cliente ci conferisce un mandato senza rappresentanza, ai sensi degli articoli 1703 e seguenti del Codice civile, limitato alla trasmissione della comunicazione da lui predisposta. Il cliente dichiara di essere l'intestatario del contratto, o di essere autorizzato ad agire per suo conto, e che i dati forniti sono veritieri.</p>
<p>Per l'invio il cliente fornisce: la lettera di disdetta firmata, una copia di un documento d'identità in corso di validità e la delega scritta che ci autorizza a trasmettere la comunicazione in suo nome. Questi documenti vengono allegati alla PEC, perché molti operatori li richiedono per accettare una disdetta inviata da un terzo. Alcuni operatori accettano solo comunicazioni firmate digitalmente o inviate dalla casella PEC del titolare: in questi casi lo indichiamo prima dell'ordine e non accettiamo l'incarico.</p>
<h2>4. Prezzo e pagamento</h2>
<p>Il prezzo dell'invio è indicato prima dell'ordine, attualmente 7,90 € per lettera. IVA non applicabile, articolo 293 B del Code général des impôts francese (regime di franchigia). Il pagamento avviene online tramite Stripe; non conserviamo i dati della carta.</p>
<h2>5. Esecuzione</h2>
<p>L'invio avviene di norma entro un giorno lavorativo dal pagamento. Le ricevute PEC sono inoltrate all'indirizzo e-mail indicato dal cliente non appena disponibili. La ricevuta di consegna attesta che il messaggio è stato consegnato nella casella PEC del destinatario e costituisce prova dell'invio e della data.</p>
<h2>6. Cosa non possiamo garantire</h2>
<p>Non siamo responsabili delle decisioni dell'operatore, dei tempi con cui gestisce la disdetta, di eventuali costi o penali previsti dal contratto del cliente, né di errori nei dati forniti dal cliente. Le schede informative sono verificate sulle fonti indicate alla data riportata, ma le condizioni degli operatori possono cambiare: in caso di dubbio fa fede il contratto del cliente. Il servizio non costituisce consulenza legale.</p>
<h2>7. Rimborso</h2>
<p>Se la PEC non viene consegnata al destinatario per causa a noi imputabile, oppure perché l'indirizzo riportato nella nostra scheda risulta errato, rimborsiamo integralmente l'importo pagato, su richiesta a info@disdettaabbonamento.it entro 30 giorni dall'ordine.</p>
<h2>8. Diritto di recesso</h2>
<p>Il consumatore dispone di 14 giorni per recedere dall'acquisto, ai sensi dell'articolo 52 del Codice del consumo. Il diritto di recesso non si applica una volta che il servizio è stato completamente eseguito, se l'esecuzione è iniziata con l'accordo espresso del consumatore e con la sua accettazione della perdita del diritto di recesso (articolo 59, lettera a, del Codice del consumo). Al momento dell'ordine il cliente chiede espressamente l'invio immediato.</p>
<h2>9. Dati personali</h2>
<p>Il trattamento dei dati è descritto nell'<a href="/privacy/">informativa privacy</a>.</p>
<h2>10. Legge applicabile e reclami</h2>
<p>Per qualsiasi problema scrivici a info@disdettaabbonamento.it: rispondiamo entro 2 giorni lavorativi. Restano salve le tutele inderogabili previste dalla legge del Paese di residenza del consumatore e la competenza del giudice del luogo di residenza o domicilio del consumatore.</p>'''
PRIVACY_HTML = r'''<h1>Informativa privacy</h1>
<p class="src">Versione del 26 ottobre 2026, ai sensi del Regolamento (UE) 2016/679 (GDPR).</p>
<h2>Titolare del trattamento</h2>
<p>Louis Lardeux, imprenditore individuale, SIREN 999 443 880, Francia. Contatto: <a href="mailto:info@disdettaabbonamento.it">info@disdettaabbonamento.it</a>.</p>
<h2>Generatore di lettere gratuito</h2>
<p>Il generatore funziona interamente nel tuo browser: i dati che inserisci non vengono inviati né salvati sui nostri server. Non usiamo cookie di profilazione né strumenti pubblicitari.</p>
<h2>Servizio di invio via PEC</h2>
<p><strong>Dati trattati:</strong> nome e cognome, indirizzo, codice fiscale se lo indichi, dati del contratto da disdire, indirizzo e-mail, lettera firmata, copia del documento d'identità e delega, dati dell'ordine. La copia del documento d'identità è usata solo per allegarla alla disdetta, come richiesto dagli operatori. I dati della carta sono trattati solo da Stripe.</p>
<p><strong>Finalità e base giuridica:</strong> esecuzione del servizio richiesto (articolo 6, paragrafo 1, lettera b, GDPR); adempimento di obblighi contabili e fiscali (lettera c); difesa dei nostri diritti in caso di contestazione (lettera f).</p>
<p><strong>Destinatari:</strong> l'operatore a cui è indirizzata la disdetta; i fornitori che ci aiutano a erogare il servizio, nominati responsabili del trattamento: Stripe per i pagamenti, il gestore PEC per l'invio, i fornitori di hosting e di posta elettronica. Non vendiamo né cediamo i tuoi dati.</p>
<p><strong>Conservazione:</strong> lettere e ricevute PEC per 24 mesi dall'invio, come prova dell'esecuzione; dati di fatturazione per 10 anni come previsto dalla legge.</p>
<h2>I tuoi diritti</h2>
<p>Puoi chiedere accesso, rettifica, cancellazione, limitazione, portabilità e opporti al trattamento (articoli 15-22 GDPR) scrivendo a info@disdettaabbonamento.it. Puoi anche presentare reclamo al Garante per la protezione dei dati personali (garanteprivacy.it) o all'autorità francese CNIL (cnil.fr).</p>
<h2>Cookie</h2>
<p>Il sito non utilizza cookie di profilazione. Eventuali strumenti tecnici necessari al funzionamento non richiedono consenso.</p>'''

def page(title, desc, path, body, schema=None, sticky=""):
    canon = DOMAIN + path
    bodycls = ' class="has-sticky"' if sticky else ""
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in (schema or []))
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canon}"><meta property="og:locale" content="it_IT">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta property="og:image" content="https://disdettaabbonamento.it/og.png"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="/style.css">{ld}</head><body{bodycls}>
<header class="top"><div class="wrap"><a class="logo" href="/"><i>✉</i><span class="lt">Disdetta<span>Abbonamento</span>.it</span></a>
<nav class="main"><a href="/telefonia/">Telefonia</a><a href="/luce-gas/">Luce e gas</a><a href="/assicurazioni/">Assicurazioni</a><a href="/guide/">Guide</a><a class="cta" href="/#cerca"><span class="lg">Trova il tuo operatore</span><span class="sm">Cerca</span></a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap"><p><a href="/">Home</a><a href="/guide/">Guide</a><a href="/come-funziona/">Come funziona</a><a href="/chi-siamo/">Chi siamo</a><a href="/note-legali/">Note legali</a><a href="/termini/">Termini e condizioni</a><a href="/privacy/">Privacy</a></p>
<p>{SITE} è un servizio indipendente, non affiliato agli operatori citati. I marchi appartengono ai rispettivi proprietari. Le informazioni sono verificate sulle fonti ufficiali alla data indicata in ogni pagina: controlla sempre il tuo contratto.</p></div></footer>
{sticky}<script src="/app.js" defer></script></body></html>"""


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
    verif = data_it(b["data_verifica"]); uff = b.get("affidabilita") == "ufficiale"
    body = '<section class="hero small">'
    body += f'<p class="crumbs"><a href="/">Home</a> › <a href="/{cat["slug"]}/">{E(cat["nome"])}</a> › {E(n)}</p>'
    body += f'<span class="pill">{"<b>✓</b> Verificato su fonte ufficiale" if uff else "Verificato su fonti di settore"} · {verif}</span>'
    body += f"<h1>Disdetta {E(n)}: <em>{'PEC, indirizzo e lettera pronta' if lettera else 'come annullare in pochi clic'}</em></h1>"
    body += (f'<p class="lead">Dove inviare la disdetta, con quale preavviso e quanto costa. Poi compili la lettera gratis in un minuto e la invii tu.</p>'
             if lettera else f'<p class="lead">{E(n)} si disdice online, senza lettere. Ecco i passaggi, il preavviso e cosa succede dopo.</p>')
    if lettera:
        body += '<a class="btn shine" href="#lettera-disdetta">Genera la lettera gratis →</a><a class="btn sec" href="#invio">Te la inviamo noi via PEC</a>'
    body += '<ul class="chips"><li>Lettera gratis</li><li>Invio PEC con ricevuta legale a 7,90 €</li><li>Fonti ufficiali citate</li></ul></section>'
    if b.get("pec"):
        facts[0] = ("PEC", f'<span class="pec">{E(b["pec"])}</span> <button class="copy" type="button" onclick="copiaPec(this,\'{E(b["pec"])}\')">Copia</button>')
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
    body += f'<div class="rv box" id="dati"><h2>Disdetta {E(n)} in breve</h2><dl class="facts">{dl}</dl></div>'
    gg = re.search(r"(\d+)\s*giorni", b.get("preavviso", "") or "")
    if lettera and gg:
        body += f'<div class="urg rv"><span class="ic">⏰</span><span><b>Se invii oggi, il contratto termina il <span id="scad" data-giorni="{gg.group(1)}">…</span></b><p>Con {gg.group(1)} giorni di preavviso ogni giorno di attesa sposta la fine del contratto. Aspettare una settimana vuol dire pagare fino al <span id="scad2">…</span>, spesso un mese in più.</p></span><a class="btn" href="#lettera-disdetta">Disdici ora →</a></div>'

    if b.get("note"):
        body += f'<div class="note"><strong>Da sapere.</strong> {E(b["note"])}</div>'
    if lettera:
        body += f'<h2>Come disdire {E(n)} in 3 passaggi</h2><div class="rv steps"><div class="step"><div class="n">1</div><h3>Compila la lettera</h3><p>Nome, indirizzo e codice cliente: la lettera si genera qui sotto.</p></div><div class="step"><div class="n">2</div><h3>Firma e allega il documento</h3><p>Aggiungi la firma e una copia del documento d\'identità.</p></div><div class="step"><div class="n">3</div><h3>Invia {"via PEC" if b.get("pec") else "con raccomandata A/R"}</h3><p>All\'indirizzo indicato sopra. Conserva la ricevuta: è la prova della data.</p></div></div>'
    body += f"<h2>Tutti i canali per disdire {E(n)}</h2><ul class=\"canali\">{canali}</ul>"
    if lettera:
        via = "PEC" if b.get("pec") else "raccomandata A/R"
        body += f"""<section class="gen" id="lettera-disdetta"><h2>Lettera di disdetta {E(n)}, gratis</h2>
<p class="sub">Compila i campi, la lettera si genera qui sotto. Puoi copiarla o salvarla in PDF e inviarla via {via}. I dati restano sul tuo dispositivo, non vengono inviati a nessuno.</p>
<form id="form-lettera" onsubmit="return genLettera()">
<div class="row2"><div><label for="nome">Nome e cognome dell'intestatario</label><input id="nome" name="nome" autocomplete="name"></div>
<div><label for="cf">Codice fiscale (facoltativo)</label><input id="cf" name="cf"></div></div>
<label for="indirizzo">Indirizzo di residenza</label><input id="indirizzo" name="indirizzo" autocomplete="street-address">
<div class="row2"><div><label for="codice">Codice cliente o numero di contratto</label><input id="codice" name="codice"></div>
<div><label for="linea">{E(CAMPO[b["categoria"]].capitalize())} (facoltativo)</label><input id="linea" name="linea"></div></div>
<div class="row2"><div><label for="luogo">Città</label><input id="luogo" name="luogo" autocomplete="address-level2"></div><div><label for="email">E-mail per la conferma (facoltativa)</label><input id="email" name="email" type="email" autocomplete="email"></div></div>
<button class="btn" type="submit">Genera la lettera →</button><p class="secure">🔒 Nessun dato viene inviato o salvato: tutto resta nel tuo browser.</p></form>
<div id="lettera"></div>
<div id="azioni" class="noprint" style="display:none"><button class="btn" type="button" onclick="copiaLettera(this)">Copia il testo</button><button class="btn sec" type="button" onclick="window.print()">Salva in PDF / stampa</button>
<p class="src">Per una disdetta con valore legale, invia la lettera firmata con copia del documento d'identità da una casella PEC, oppure con raccomandata A/R, e conserva la ricevuta.</p></div>
<script>window.LETTERA={json.dumps({"azienda": n, "pec": b.get("pec", ""), "postale": b.get("indirizzo_postale", "") or ("[indirizzo del tuo club, indicato nel contratto]" if b["categoria"] == "palestre" else ""), "servizio": cat["servizio"], "legge": LEGGE_BREVE.get(b["categoria"], ""), "campo": CAMPO[b["categoria"]], "cat": b["categoria"]}, ensure_ascii=False)}</script>
</section>"""
    if lettera:
        body += PLANS
    rel = [g for g in GUIDE if b["categoria"] in g["cats"]][:3]
    if rel:
        body += '<h2>Guide utili</h2><div class="grid">' + "".join(f'<a class="card" href="/guide/{g["slug"]}/"><span class="av altri-servizi">📘</span><span><b>{E(g["h1"])}</b><small>Guida</small></span></a>' for g in rel) + '</div>'
    body += f"<h2>Cosa dice la legge</h2><p>{E(cat['legge'])}</p>"
    faqs = faq_brand(b, cat)
    if faqs:
        body += "<h2>Domande frequenti</h2>" + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    if peers:
        body += f"<h2>Altre disdette: {E(cat['nome'].lower())}</h2><div class=\"grid\">" + "".join(
            card(p) for p in peers) + "</div>"
    host = lambda u: re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
    _seen = {}
    for u in b.get("fonti", []):
        _seen.setdefault(host(u), u)
    fonti = " · ".join(f'<a href="{E(u)}" rel="nofollow noopener" target="_blank">{E(h)}</a>' for h, u in _seen.items())
    body += f'<div class="why"><span>🛡️</span><span><b>Perché fidarsi di questa scheda</b>Indirizzi e condizioni sono presi dai documenti {"ufficiali di " + E(n) if uff else "pubblicati"} e verificati il {verif}. Fonti: {fonti}. Le condizioni possono cambiare: in caso di dubbio fa fede il tuo contratto.</span></div>'
    schema = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}] if faqs else []
    schema.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": cat["nome"], "item": f"{DOMAIN}/{cat['slug']}/"},
        {"@type": "ListItem", "position": 3, "name": f"Disdetta {n}", "item": DOMAIN + path}]})
    if lettera:
        body += f'<section class="band"><h2>Disdici {E(n)} oggi</h2><p>Lettera gratis in un minuto, oppure te la inviamo noi in PEC con ricevuta legale.</p><a class="btn shine" href="#lettera-disdetta">Genera la lettera gratis →</a></section>'
    sticky = '<div class="sticky"><a class="btn" href="#lettera-disdetta">Genera la lettera gratis →</a></div>' if lettera else ''
    write(path, page(title, desc, path, body, schema, sticky))
    return path


def etichetta(b):
    return "PEC e lettera pronta" if b.get("pec") else ("raccomandata e lettera pronta" if (b.get("indirizzo_postale") or b["categoria"] == "palestre") else "si disdice online")


def iniziali(n):
    w = re.findall(r"[A-Za-z0-9]+", n)
    return (w[0][:2] if len(w) == 1 else w[0][0] + w[1][0]).upper() if w else "?"


def card(b):
    return (f'<a class="card" data-nome="{E(b["nome"].lower())}" href="/disdetta-{b["slug"]}/"><span class="av {b["categoria"]}">{E(iniziali(b["nome"]))}</span><span><b>Disdetta {E(b["nome"])}</b>'
            f'<small>{etichetta(b)}</small></span></a>')


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    brands = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "brands-*.json"))):
        if os.path.basename(f).startswith("brands-2-") and not os.path.exists(f + ".ok"):
            continue
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
        body = f'<section class="hero small"><p class="crumbs"><a href="/">Home</a> › {E(cat["nome"])}</p><h1>Disdetta <em>{E(cat["nome"].lower())}</em></h1><p class="lead">{E(cat["intro"])}</p><ul class="chips"><li>{len(lst)} operatori verificati</li><li>Lettere gratuite o invio PEC per te</li><li>Fonti ufficiali citate</li></ul></section>'
        body += '<div class="grid">' + "".join(card(b) for b in lst) + "</div>"
        body += f"<h2>Cosa dice la legge</h2><p>{E(cat['legge'])}</p>"
        write(p, page(f"Disdetta {cat['nome'].lower()}: PEC, indirizzi e moduli ({TODAY[:4]})",
                      f"Come disdire {cat['nome'].lower()}: indirizzi PEC e postali, preavviso e lettere di disdetta gratuite per {len(lst)} operatori, verificati sulle fonti ufficiali.", p, body))
        urls.append(p)
    # guide
    gcards = []
    for g in GUIDE:
        gp = f"/guide/{g['slug']}/"
        rel = [b for b in brands if b["categoria"] in g["cats"]][:9]
        body = f'<section class="hero small"><p class="crumbs"><a href="/">Home</a> › <a href="/guide/">Guide</a> › {E(g["h1"])}</p><span class="pill"><b>✓</b> Aggiornata il {data_it(TODAY)}</span><h1>{E(g["h1"])}</h1></section>'
        body += '<article class="guide">' + g["body"] + '</article>'
        body += '<section class="band"><h2>Pronto a disdire?</h2><p>Cerca il tuo operatore: indirizzo verificato e lettera pronta in un minuto.</p><a class="btn shine" href="/#cerca">Trova il tuo operatore →</a></section>'
        if rel:
            body += '<h2>Operatori collegati</h2><div class="grid">' + "".join(card(b) for b in rel) + '</div>'
        sch = [{"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "dateModified": TODAY, "inLanguage": "it-IT",
                "author": {"@type": "Organization", "name": SITE}, "publisher": {"@type": "Organization", "name": SITE}, "mainEntityOfPage": DOMAIN + gp}]
        write(gp, page(g["title"], g["desc"], gp, body, sch)); urls.append(gp)
        gcards.append(f'<a class="card" href="{gp}"><span class="av altri-servizi">📘</span><span><b>{E(g["h1"])}</b><small>{E(g["desc"][:80])}…</small></span></a>')
    body = '<section class="hero small"><p class="crumbs"><a href="/">Home</a> › Guide</p><h1>Guide alla <em>disdetta</em></h1><p class="lead">Leggi, canali di invio, casi particolari e cosa fare se l\'operatore non risponde.</p></section><div class="grid">' + "".join(gcards) + '</div>'
    write("/guide/", page("Guide alla disdetta: leggi, PEC, raccomandata e casi particolari", "Tutte le guide per disdire un contratto: legge Bersani, come inviare una PEC, trasloco, decesso, recesso entro 14 giorni, reclami e conciliazioni.", "/guide/", body)); urls.append("/guide/")
    # home
    nuff = sum(1 for b in brands if b.get("affidabilita") == "ufficiale")
    body = '<section class="hero home" id="cerca"><div><span class="pill"><b>✓</b> Aggiornato il ' + data_it(TODAY) + '</span>'
    body += '<h1>Disdici qualsiasi abbonamento <em>in un minuto</em></h1>'
    body += '<p class="lead">Trova l\'indirizzo PEC o postale giusto del tuo operatore, controlla preavviso e costi, e genera gratis la lettera di disdetta pronta da inviare.</p>'
    body += '<div class="searchbox"><input class="search" type="search" placeholder="Cerca il tuo operatore: TIM, Sky, Enel, McFit…" autocomplete="off" aria-label="Cerca un operatore"></div>'
    body += '<ul class="chips"><li>Lettera gratis, senza registrazione</li><li>Indirizzi verificati sui documenti ufficiali</li><li>Invio PEC con ricevuta legale</li></ul>'
    body += f'<div class="stats"><div><b data-count="{len(brands)}">{len(brands)}</b><span>operatori</span></div><div><b data-count="{nuff}">{nuff}</b><span>schede da fonte ufficiale</span></div><div><b>1 min</b><span>per la lettera</span></div><div><b>7,90 €</b><span>invio PEC per te</span></div></div></div>' + demo_html(brands)
    body += '<h2>Come funziona</h2><div class="rv steps"><div class="step"><div class="n">1</div><h3>Cerca l\'operatore</h3><p>Trovi PEC, indirizzo per la raccomandata, preavviso e costi, con la data di verifica.</p></div><div class="step"><div class="n">2</div><h3>Compila la lettera</h3><p>Inserisci i tuoi dati: la lettera di disdetta si genera subito, con i riferimenti di legge.</p></div><div class="step"><div class="n">3</div><h3>Inviala e conserva la ricevuta</h3><p>Via PEC o raccomandata A/R. La ricevuta di consegna è la prova della disdetta.</p></div></div><p style="text-align:center"><a class="btn shine" href="#cerca">Inizia ora, è gratis →</a></p>'
    ICONE = {"telefonia": "📶", "tv-streaming": "📺", "energia": "💡", "assicurazioni": "🛡️", "palestre": "🏋️", "altri-servizi": "🧾"}
    body += '<h2>Scegli la categoria</h2><div class="rv cats">' + "".join(f'<a class="cat" href="/{CATEGORIE[c]["slug"]}/"><div class="ic">{ICONE[c]}</div><h3>{E(CATEGORIE[c]["nome"])}</h3><small>{len(bycat[c])} operatori</small></a>' for c in CATEGORIE if c in bycat) + '</div>'
    body += '<div id="operatori">'
    for c in CATEGORIE:
        if c in bycat:
            cat = CATEGORIE[c]
            body += f'<h2><a href="/{cat["slug"]}/" style="color:inherit;text-decoration:none">{E(cat["nome"])}</a></h2><div class="grid">' + "".join(card(b) for b in bycat[c]) + "</div>"
    body += '</div>'
    body += '<h2>Perché usare Disdetta Abbonamento</h2><div class="rv trust"><div><h3>🔎 Indirizzi verificati</h3><p>Ogni PEC e indirizzo viene dai documenti dell\'operatore, con fonte e data di verifica in ogni scheda.</p></div><div><h3>⚖️ Lettera con valore legale</h3><p>Il testo cita le norme giuste (come la legge Bersani per la telefonia) e chiede lo stop di ogni addebito.</p></div><div><h3>🔒 Privacy totale</h3><p>La lettera si genera nel tuo browser. Non chiediamo registrazione e non salviamo i tuoi dati.</p></div></div>'
    body += '<h2>Le nostre guide</h2><div class="grid rv">' + ''.join(gcards[:6]) + '</div><p><a href="/guide/">Tutte le guide →</a></p>'
    body += REVIEWS
    body += '<section class="band"><h2>Pronto a disdire?</h2><p>Cerca il tuo operatore e prepara la lettera adesso, è gratis.</p><a class="btn shine" href="#cerca">Trova il tuo operatore →</a></section>'
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
        "/privacy/": ("Privacy", "Informativa privacy di Disdetta Abbonamento: quali dati trattiamo, perché e per quanto tempo.", PRIVACY_HTML),
        "/termini/": ("Termini e condizioni", "Termini e condizioni del servizio di invio della disdetta via PEC di Disdetta Abbonamento.", TERMINI_HTML),
    }
    for p, (t, d, b) in statiche.items():
        write(p, page(f"{t} | {SITE}", d, p, b)); urls.append(p)
    open(os.path.join(OUT, "style.css"), "w").write(CSS)
    open(os.path.join(OUT, "app.js"), "w").write(JS)
    json.dump([{"n": b["nome"], "u": f"/disdetta-{b['slug']}/", "c": CATEGORIE[b["categoria"]]["nome"], "cc": b["categoria"], "i": iniziali(b["nome"]), "l": etichetta(b)} for b in brands],
              open(os.path.join(OUT, "operatori.json"), "w", encoding="utf-8"), ensure_ascii=False)
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    sm = "".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    for src, dst in [("brand/icon-512.png", "favicon.png"), ("brand/icon-512.png", "apple-touch-icon.png"), ("brand/og.png", "og.png")]:
        if os.path.exists(os.path.join(ROOT, src)):
            shutil.copy(os.path.join(ROOT, src), os.path.join(OUT, dst))
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(page("Pagina non trovata | " + SITE, "Pagina non trovata.", "/404.html",
        '<section class="hero small"><h1>Pagina <em>non trovata</em></h1><p class="lead">La pagina che cerchi non esiste o è stata spostata. Cerca il tuo operatore:</p><div class="searchbox"><input class="search" type="search" placeholder="TIM, Sky, Enel, McFit…" autocomplete="off" aria-label="Cerca un operatore"></div></section><p><a class="btn" href="/">Torna alla home</a></p>').replace('<link rel="canonical" href="https://disdettaabbonamento.it/404.html">', '<meta name="robots" content="noindex">'))
    rp = os.path.join(ROOT, "data", "redirects.json")
    if os.path.exists(rp):
        for old, new in json.load(open(rp)).items():
            dst = os.path.join(OUT, old.lstrip("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            u = DOMAIN + new
            open(dst, "w", encoding="utf-8").write(f'<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Pagina spostata</title><link rel="canonical" href="{u}"><meta http-equiv="refresh" content="0; url={u}"><script>location.replace("{u}")</script></head><body><p>Questa pagina è stata spostata: <a href="{u}">{u}</a></p></body></html>')
    open(os.path.join(OUT, "CNAME"), "w").write("disdettaabbonamento.it\n")
    k = open(os.path.join(ROOT, "_build", "indexnow.key")).read().strip()
    open(os.path.join(OUT, k + ".txt"), "w").write(k)
    open(os.path.join(ROOT, "_build", "urls.txt"), "w").write("\n".join(DOMAIN + u for u in urls) + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print(f"{len(brands)} marchi, {len(urls)} pagine -> {OUT}")


if __name__ == "__main__":
    main()
