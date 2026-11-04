#!/usr/bin/env python3
"""Generatore statico di disdettaabbonamento.it.
Legge data/brands-*.json e scrive il sito in site/.
Uso : python3 _build/build.py
"""
import json, glob, os, html, re, shutil, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guide import GUIDE
_ap = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "approfondimenti.json")
APPROF = json.load(open(_ap, encoding="utf-8")) if os.path.exists(_ap) else {}

def seal(txt="RICEVUTA LEGALE • PEC CERTIFICATA • "):
    return ('<div class="seal" aria-hidden="true"><svg viewBox="0 0 120 120"><defs><path id="sc" d="M60,60 m-46,0 a46,46 0 1,1 92,0 a46,46 0 1,1 -92,0"/></defs>'
            '<circle cx="60" cy="60" r="58" fill="#fff" stroke="#e1e6ef"/><text font-family="system-ui,sans-serif" font-size="11" font-weight="800" letter-spacing="1.2" textLength="285" lengthAdjust="spacing" fill="#0b7a4f"><textPath href="#sc">' + txt + '</textPath></text></svg><div class="c">✓</div></div>')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
DOMAIN = "https://disdettaabbonamento.it"
SITE = "Disdetta Abbonamento"
TODAY = dt.date.today().isoformat()
ASSET_V = None  # rempli au build
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

CSS = """.inbreve{background:#fff;border:1px solid #e3e3df;border-left:4px solid #0a7a4b;border-radius:10px;padding:12px 16px;margin:14px 0 6px;font-size:15px;line-height:1.5}.inbreve .pec{word-break:break-all}
.launch{margin:-4px 0 12px;font-size:14px;color:#6b3b12;background:#fff4e5;border:1px solid #ffd2b8;border-radius:8px;padding:6px 10px}.launch b{color:#b4530a}
.tl{list-style:none;margin:10px 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:4px 10px;font-size:13px;color:var(--muted)}.tl li{line-height:1.35}
.urg .dl{margin-top:12px;font-size:14.5px;color:#6b3b12}.urg .dl label{display:block;font-weight:600;margin-bottom:6px}.urg .dlrow{display:flex;gap:8px;flex-wrap:wrap}.urg .dlrow input{font:inherit;padding:10px 12px;border:1px solid #ffd2b8;border-radius:10px;background:#fff;min-width:170px}.urg .dlrow .btn{padding:10px 16px;width:auto;margin:0}.urg .dlout{display:none;margin:10px 0 0;background:#fff;border-radius:10px;padding:10px 12px;color:var(--fg);font-size:15px}
.guide .dl{margin:10px 0 18px;padding:14px;border:1px solid var(--line);border-radius:12px;background:var(--soft)}.guide .dl label{display:block;font-weight:600;margin-bottom:6px}.guide .dlrow{display:flex;gap:8px;flex-wrap:wrap}.guide .dlrow input,.guide .dlrow select{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;min-width:170px}.guide .dlout{display:none;margin:10px 0 0;background:#fff;border-radius:10px;padding:10px 12px;font-size:15px}.guide-letter{border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:14px 18px;background:#fff;font-size:15px}
.urgbtns{display:flex;flex-direction:column;gap:8px;margin-left:auto;flex:none}.urgbtns .btn{margin:0;justify-content:center}
.pecbox{margin-top:18px;background:linear-gradient(120deg,#eef3ff,#f7f9ff);border:1px solid #c9d8ff;border-radius:16px;padding:18px 20px;display:grid;gap:12px}.pecbox b{display:block;font-size:18px;margin-bottom:4px}.pecbox span{color:var(--muted);font-size:15px;line-height:1.5}.pecbox .btn{justify-content:center}
.cd{display:inline-block;margin-left:6px;font-weight:700;color:#b4530a}
.co-steps{list-style:none;display:flex;gap:8px;flex-wrap:wrap;padding:0;margin:18px 0 0}.co-steps li{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 14px 6px 6px;font-size:14.5px;color:var(--muted)}.co-steps li b{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--soft);color:var(--muted);font-size:13px}.co-steps li.on{color:var(--fg);border-color:var(--accent)}.co-steps li.on b{background:var(--accent);color:#fff}
.gen label.chk{display:flex;flex-direction:row;gap:10px;align-items:flex-start;font-size:14.5px;margin:14px 0 16px;font-weight:500;line-height:1.45}.gen label.chk input{margin:2px 0 0;width:18px;height:18px;flex:none;padding:0}
.sig{display:grid;gap:10px;margin:8px 0 14px}.sig canvas{width:100%;height:auto;aspect-ratio:3/1;background:#fff;border:2px dashed var(--line);border-radius:14px;touch-action:none;cursor:crosshair}.sig .btn{justify-self:start;padding:8px 14px}
.co-prev{margin:0 0 16px}.co-prev pre{white-space:pre-wrap;font:14px/1.5 inherit;background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px;margin:10px 0}.co-err{color:#b42318;font-weight:600}.co-list{font-size:16px;line-height:1.8;padding-left:4px;list-style:none}.co-up{font-size:15px;line-height:1.6;padding-left:20px;margin:6px 0 14px}.co-up i{font-style:normal;background:var(--soft);padding:1px 6px;border-radius:6px;word-break:break-all}
.co-after{font-size:14.5px;color:var(--muted);margin-top:14px}
.trustbar{background:#0f1b33;color:#fff;font-size:13.5px;overflow:hidden;white-space:nowrap;line-height:34px;height:34px}.tb-track{display:inline-flex;animation:tbscroll 45s linear infinite;will-change:transform}.tb-track span{flex:none;padding-right:44px}.trustbar:hover .tb-track{animation-play-state:paused}@keyframes tbscroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}@media (prefers-reduced-motion:reduce){.tb-track{animation:none}}.pricechart{margin:28px 0 8px;padding:22px 22px 18px;border:1px solid var(--line);border-radius:var(--radius);background:linear-gradient(180deg,#fff,var(--soft));box-shadow:var(--shadow)}.pc-head h2{margin:0 0 4px}.pc-head p{margin:0 0 16px;color:var(--muted)}.pc-row{display:grid;grid-template-columns:minmax(180px,34%) 1fr;gap:14px;align-items:center;margin:12px 0}.pc-lab b{display:block;font-size:15px}.pc-lab small{color:var(--muted);font-size:13px}.pc-bar{position:relative;height:34px;background:var(--line);border-radius:10px;overflow:hidden}.pc-bar span{position:absolute;inset:0 auto 0 0;width:var(--w);border-radius:10px;background:#9aa6bd;transform-origin:left;transform:scaleX(0);transition:transform 1.2s cubic-bezier(.2,.7,.2,1)}.pricechart.in .pc-bar span{transform:scaleX(1)}.pricechart.in .pc-row:nth-of-type(2) .pc-bar span{transition-delay:0.15s}.pricechart.in .pc-row:nth-of-type(3) .pc-bar span{transition-delay:0.30s}.pricechart.in .pc-row:nth-of-type(4) .pc-bar span{transition-delay:0.45s}.pricechart.in .pc-row:nth-of-type(5) .pc-bar span{transition-delay:0.60s}.pricechart.in .pc-row:nth-of-type(6) .pc-bar span{transition-delay:0.75s}.pricechart.in .pc-row:nth-of-type(7) .pc-bar span{transition-delay:0.90s}.pc-row.acc .pc-bar span::after{content:"";position:absolute;inset:0;border-radius:10px;background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,.45) 50%,transparent 70%);background-size:220% 100%;animation:pcshine 2.8s ease-in-out 1.6s infinite}@keyframes pcshine{0%{background-position:120% 0}60%,100%{background-position:-120% 0}}.pc-bar em{opacity:0;transition:opacity .4s ease .9s}.pricechart.in .pc-bar em{opacity:1}.pc-badge{display:inline-block;margin-left:8px;padding:2px 8px;border-radius:999px;background:#e8fff1;color:#0b7a4f;font-size:12px;font-weight:700;vertical-align:middle;transform:scale(.6);opacity:0;transition:transform .45s cubic-bezier(.3,1.6,.5,1) 1.4s,opacity .3s ease 1.4s}.pricechart.in .pc-badge{transform:scale(1);opacity:1}.pc-row.acc .pc-bar span{background:linear-gradient(90deg,var(--accent),#4f86ff)}.pc-bar em{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-style:normal;font-weight:700;color:#fff;font-size:14.5px}.pc-row.acc .pc-lab b{color:var(--accent-d)}.pc-note{margin:14px 0 0;font-size:14px;color:var(--muted)}@keyframes pcgrow{from{transform:scaleX(0)}to{transform:scaleX(1)}}@media (max-width:640px){.pc-row{grid-template-columns:1fr;gap:6px}}@media (prefers-reduced-motion:reduce){.pc-bar span{transition:none;transform:none}.pc-bar em,.pc-badge{transition:none;opacity:1;transform:none}.pc-row.acc .pc-bar span::after{animation:none}}.founder{display:flex;gap:16px;align-items:center;margin:14px 0 18px}.founder img{border-radius:12px;object-fit:cover;flex:none}.founder b{display:block;font-size:17px}.founder span{display:block;color:var(--muted);font-size:14.5px}.founder p{margin:8px 0 0}.founder.mini{margin:14px 0 0;padding-top:12px;border-top:1px solid var(--line)}.founder.mini img{border-radius:50%;width:48px;height:48px}.founder.mini b{font-size:15px}.upsell .legale{margin:10px 0 4px;font-size:14px;color:var(--muted)}.upsell .legale b.inl{display:inline;font-size:inherit;margin:0;color:var(--fg)}.upsell .urgente{margin:12px 0 4px;font-size:14.5px;font-weight:600;color:#8a4b00}.upsell .passi{margin:8px 0 12px 18px;padding:0;font-size:14.5px}.upsell .passi li{margin:2px 0}.upsell{margin-top:18px;border:2px solid var(--accent);border-radius:16px;padding:18px 20px;background:#fff;transform:translateY(10px);opacity:0;transition:transform .4s cubic-bezier(.2,.7,.2,1),opacity .4s ease}.upsell.in{transform:none;opacity:1}.upsell b{display:block;font-size:19px;margin-bottom:10px}.upsell table{width:100%;border-collapse:collapse;font-size:14.5px;margin-bottom:14px}.upsell th,.upsell td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:top}.upsell th:last-child,.upsell td:last-child{color:var(--ok);font-weight:600}.upsell td:first-child{color:var(--muted);width:28%}.upsell .btn{width:100%;justify-content:center;margin:0}.scelta{margin:14px 0 22px}.sc-q{margin:0 0 12px;font-size:15.5px}.sc-grid{display:grid;grid-template-columns:1.15fr 1fr;gap:14px}.sc{position:relative;border:1px solid var(--line);border-radius:16px;padding:18px;background:#fff;display:flex;flex-direction:column;gap:8px}.sc.pro{border:2px solid var(--accent);box-shadow:var(--shadow)}.sc h3{margin:0;font-size:17px}.sc .price{font-size:24px;font-weight:800}.sc .price small{font-size:13px;font-weight:500;color:var(--muted)}.sc ul{list-style:none;margin:0;padding:0;font-size:14.5px;display:grid;gap:5px;flex:1;align-content:start}.sc .btn{justify-content:center;margin:4px 0 0}.sc small{color:var(--muted);font-size:12.5px;text-align:center}.sc .tag{align-self:flex-start;background:var(--accent);color:#fff;font-size:12px;font-weight:700;padding:3px 9px;border-radius:999px}@media (max-width:640px){.sc-grid{grid-template-columns:1fr}}
.proof{margin:12px 0 0;font-size:14.5px;color:var(--muted)}.proof b{color:var(--fg)}
.after{margin:14px 0 0;padding:0 0 0 20px;font-size:14px;color:var(--muted);line-height:1.5}.after li{margin:4px 0}.after b{color:var(--fg)}
.ctabar{display:flex;align-items:center;gap:16px;flex-wrap:wrap;background:var(--soft);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:22px 0}.ctabar>span:first-child{flex:1;min-width:220px;font-size:15px;color:var(--muted);line-height:1.5}.ctabar b{color:var(--fg)}.ctabar .btn{margin:0;flex:none}.ctabar .ctab{display:flex;gap:8px;flex-wrap:wrap}.ctabar.alt{background:linear-gradient(120deg,#eef3ff,#f7f9ff);border-color:#c9d8ff}
.slidein{position:fixed;right:16px;bottom:16px;z-index:40;width:min(340px,calc(100vw - 32px));background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);padding:18px 18px 14px;transform:translateY(24px);opacity:0;transition:transform .45s cubic-bezier(.2,.7,.2,1),opacity .45s ease}.slidein.in{transform:none;opacity:1}.slidein b{display:block;font-size:17px;margin-bottom:4px;padding-right:24px}.slidein p{margin:0 0 12px;font-size:14.5px;color:var(--muted);line-height:1.5}.slidein .btn{width:100%;justify-content:center;margin:0}.slidein small{display:block;margin-top:8px;font-size:12.5px;color:var(--muted);text-align:center}.slidein .x{position:absolute;top:8px;right:10px;border:0;background:none;font-size:22px;line-height:1;color:var(--muted);cursor:pointer}
@media(max-width:820px){.slidein{display:none}.ctabar .btn{width:100%;justify-content:center}.ctabar .ctab{width:100%}.ctabar .ctab .btn{flex:1}}
.sticky.two{display:none;grid-template-columns:1fr 1.4fr;gap:8px}.sticky.two .btn{width:100%;padding:12px 10px;font-size:15px}
@media(max-width:820px){.urgbtns{width:100%;margin:8px 0 0}.tl{grid-template-columns:1fr}.sticky.two{display:grid}}

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
.guar.home div{font-size:15px;line-height:1.5;padding:18px}.guar.home b{font-size:17px;margin-bottom:6px}.guar.home a{color:var(--accent)}
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
.marquee:hover .track{animation-play-state:paused}
.seal{position:relative;width:92px;height:92px;flex:none}
.seal svg{position:absolute;inset:0;width:100%;height:100%;animation:spin 22s linear infinite}
.seal .c{position:absolute;inset:21px;border-radius:50%;background:linear-gradient(135deg,#0b7a4f,#14a06a);display:grid;place-items:center;color:#fff;font-size:22px;font-weight:900;box-shadow:0 8px 22px rgba(11,122,79,.35)}
@keyframes spin{to{transform:rotate(360deg)}}
.hero-seal{display:flex;align-items:center;gap:16px;margin-top:22px;max-width:520px}.hero-seal p{margin:0;font-size:15px;color:var(--muted)}.hero-seal b{color:var(--fg);display:block;font-size:16px}
.plan.pro .seal{position:absolute;right:-22px;top:-30px;width:96px;height:96px}.plan.pro .seal .c{inset:22px;font-size:22px}
.tstrip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin:34px 0 8px}
.tstrip div{display:flex;gap:12px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;opacity:0;transform:translateY(14px) scale(.98);transition:opacity .5s,transform .5s}
.tstrip.in div{opacity:1;transform:none}.tstrip.in div:nth-child(2){transition-delay:.12s}.tstrip.in div:nth-child(3){transition-delay:.24s}.tstrip.in div:nth-child(4){transition-delay:.36s}
.tstrip i{flex:none;width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-style:normal;font-size:20px;background:var(--accent-l)}
.tstrip b{display:block;font-size:15px}.tstrip span{font-size:13.5px;color:var(--muted)}
.box.rv .facts dt,.box.rv .facts dd{opacity:0;transform:translateX(-8px);transition:opacity .45s,transform .45s}
.box.rv.in .facts dt,.box.rv.in .facts dd{opacity:1;transform:none}
.box.rv.in .facts dd:nth-of-type(2),.box.rv.in .facts dt:nth-of-type(2){transition-delay:.1s}.box.rv.in .facts dd:nth-of-type(3),.box.rv.in .facts dt:nth-of-type(3){transition-delay:.2s}.box.rv.in .facts dd:nth-of-type(4),.box.rv.in .facts dt:nth-of-type(4){transition-delay:.3s}.box.rv.in .facts dd:nth-of-type(5),.box.rv.in .facts dt:nth-of-type(5){transition-delay:.4s}.box.rv.in .facts dd:nth-of-type(6),.box.rv.in .facts dt:nth-of-type(6){transition-delay:.5s}
.facts dt:before{content:"✓";display:inline-grid;place-items:center;width:18px;height:18px;border-radius:50%;background:var(--okbg);color:var(--ok);font-size:11px;margin-right:7px;transform:scale(0);transition:transform .35s cubic-bezier(.2,1.6,.4,1) .2s}
.box.rv.in .facts dt:before{transform:scale(1)}
.steps{position:relative}
.steps.rv:before{content:"";position:absolute;left:8%;right:8%;top:39px;height:3px;border-radius:3px;background:linear-gradient(90deg,#1f5eff,#00b4d8);transform:scaleX(0);transform-origin:left;transition:transform 1.1s ease .2s;z-index:0}
.steps.rv.in:before{transform:scaleX(1)}.step{position:relative;z-index:1}
.badge{position:relative;overflow:hidden}.badge:after{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.7) 50%,transparent 70%);transform:translateX(-120%);animation:shine 4s ease-in-out infinite}
@media(max-width:820px){.tstrip{grid-template-columns:repeat(2,minmax(0,1fr))}.steps.rv:before{display:none}.plan.pro .seal{right:-6px;top:-34px;width:84px;height:84px}}
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
(function(){var cs=document.querySelectorAll('.pricechart');if(!cs.length)return;var go=function(c){if(c.classList.contains('in'))return;c.classList.add('in');c.querySelectorAll('.pc-bar em').forEach(function(em){var t=em.textContent,m=t.match(/(\d+)(,(\d+))?/);if(!m)return;var end=parseFloat(m[1]+'.'+(m[3]||'0')),dec=m[3]?m[3].length:0,st=null;var f=function(ts){st=st||ts;var p=Math.min(1,(ts-st)/1100);em.textContent=t.replace(m[0],(end*(1-Math.pow(1-p,3))).toFixed(dec).replace('.',','));if(p<1)requestAnimationFrame(f);else em.textContent=t};setTimeout(function(){requestAnimationFrame(f)},500);setTimeout(function(){em.textContent=t},2300)})};if(!('IntersectionObserver' in window)){cs.forEach(go);return}var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){go(e.target);io.unobserve(e.target)}})},{threshold:.35});cs.forEach(function(c){io.observe(c)})})();
// Attribution : si la visite vient d'une pub (utm_source), on le note dans le lien Stripe
(function(){try{var u=new URLSearchParams(location.search);var src=u.get('utm_source')||sessionStorage.getItem('src');if(!src)return;sessionStorage.setItem('src',src);var tag='-'+src.replace(/[^a-z0-9]/gi,'').slice(0,12);document.querySelectorAll('a[href*="buy.stripe.com"]').forEach(function(a){if(a.href.indexOf('client_reference_id=')>-1&&a.href.indexOf(tag)===-1){a.href=a.href+tag;}});}catch(e){}})();

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
  document.getElementById('azioni').style.display='block'; el.scrollIntoView({behavior:'smooth',block:'start'});if(typeof upsell==='function')setTimeout(upsell,700);
  return false;
}
function calcScad(f,gg){try{var v=f.d.value;if(!v)return false;var sc=new Date(v+'T12:00:00');var lim=new Date(sc);lim.setDate(lim.getDate()-gg);var oggi=new Date();oggi.setHours(12,0,0,0);var diff=Math.round((lim-oggi)/86400000);var fmt=function(d){return d.toLocaleDateString('it-IT',{day:'numeric',month:'long',year:'numeric'})};var o=f.querySelector('.dlout');
 if(diff<0){o.innerHTML='<b>Sei oltre il termine</b>: con '+gg+' giorni di preavviso andava inviata entro il '+fmt(lim)+'. Invia comunque oggi: il recesso varrà per la scadenza successiva, e prima invii meno paghi.';}
 else if(diff===0){o.innerHTML='<b>Ultimo giorno utile: oggi.</b> Invia la disdetta entro stasera, meglio via PEC che fa fede della data.';}
 else{o.innerHTML='<b>Invia entro il '+fmt(lim)+'</b>, cioè tra '+diff+' giorn'+(diff===1?'o':'i')+'. Dopo quella data l\'operatore può considerare il contratto rinnovato.';}
 o.style.display='block';if(window.goatcounter)goatcounter.count({path:'calcolo-scadenza'+location.pathname,title:'Calcolo scadenza',event:true});}catch(e){}return false;}
(function(){document.addEventListener('click',function(e){var a=e.target.closest('a[data-pec]');if(a&&window.LETTERA){try{localStorage.setItem('ordine',JSON.stringify(Object.assign({},window.LETTERA,{pagina:location.pathname,t:Date.now()})))}catch(_){}}if(a&&window.goatcounter){goatcounter.count({path:'clic-pec'+location.pathname,title:'Clic Invia via PEC',event:true});}});var fl=document.getElementById('form-lettera');if(fl&&!document.getElementById('co-1')){fl.addEventListener('submit',function(){try{var o={};['nome','cf','indirizzo','codice','linea','luogo','email'].forEach(function(k){if(fl.elements[k])o[k]=fl.elements[k].value});localStorage.setItem('datiLettera',JSON.stringify(o));if(window.LETTERA)localStorage.setItem('ordine',JSON.stringify(Object.assign({},window.LETTERA,{pagina:location.pathname,t:Date.now()})))}catch(_){}if(window.goatcounter)goatcounter.count({path:'lettera-generata'+location.pathname,title:'Lettera generata',event:true});});}})();
(function(){document.querySelectorAll('[data-cd]').forEach(function(el){var end=new Date(el.dataset.cd+'T23:59:59');var d=Math.ceil((end-new Date())/86400000);if(d>0&&d<=45)el.textContent='Mancano '+d+' giorn'+(d===1?'o':'i')+'.';});})();
(function(){var el=document.querySelector('[data-proof]');if(!el||!window.fetch)return;var slug=el.dataset.proof;var base='https://disdetta.goatcounter.com/counter/';function g(p){return fetch(base+p+'.json').then(function(r){return r.ok?r.json():null}).catch(function(){return null})}
 Promise.all([g('/disdetta-'+slug+'/'),g('/lettera-generata/disdetta-'+slug+'/')]).then(function(r){var v=r[0]&&+r[0].count||0,l=r[1]&&+r[1].count||0;var parts=[];if(v>=50)parts.push('👀 Scheda consultata <b>'+v.toLocaleString('it-IT')+'</b> volte');if(l>=10)parts.push('✉️ <b>'+l.toLocaleString('it-IT')+'</b> lettere generate da questa pagina');if(parts.length){el.innerHTML=parts.join(' · ');el.hidden=false;}});})();
(function(){if(!('IntersectionObserver' in window)||!window.goatcounter&&!document.querySelector('[data-pec]'))return;var vu={};var io=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;var k=e.target.id||'offerta';if(vu[k])return;vu[k]=1;io.unobserve(e.target);if(window.goatcounter)goatcounter.count({path:'vista-'+k+location.pathname,title:'Offerta vista: '+k,event:true});});},{threshold:.5});['scelta','upsell'].forEach(function(id){var el=document.getElementById(id);if(el)io.observe(el);});})();
function chiudiSlide(){var s=document.getElementById('slidein');if(s){s.hidden=true;try{sessionStorage.setItem('slide','1')}catch(e){}}}
(function(){var s=document.getElementById('slidein');if(!s)return;try{if(sessionStorage.getItem('slide'))return;}catch(e){}var shown=false;function onS(){if(shown)return;var h=document.documentElement;var r=(h.scrollTop)/(h.scrollHeight-h.clientHeight);if(r>.55){shown=true;s.hidden=false;requestAnimationFrame(function(){s.classList.add('in')});if(window.goatcounter)goatcounter.count({path:'slidein-mostrato'+location.pathname,title:'Slide-in mostrato',event:true});window.removeEventListener('scroll',onS);}}window.addEventListener('scroll',onS,{passive:true});})();
(function(){if(!document.getElementById('co-1'))return;var d=null;try{d=JSON.parse(localStorage.getItem('ordine')||'null')}catch(e){}
 if(d&&d.azienda){window.LETTERA=d;document.getElementById('co-op').innerHTML='Disdetta di <b>'+d.azienda.replace(/</g,'&lt;')+'</b>'+(d.pec?', inviata in PEC a <b>'+d.pec+'</b>':'')+'.';}
 else{window.LETTERA={azienda:'',pec:'',postale:'',servizio:'al servizio indicato',legge:'',campo:'numero',cat:'altri-servizi'};document.getElementById('co-opfield').hidden=false;document.getElementById('co-azienda').required=true;document.getElementById('co-op').textContent='Indica l\'operatore che vuoi disdire.';}
 try{var dl=JSON.parse(localStorage.getItem('datiLettera')||'null');if(dl){var ff=document.getElementById('form-lettera');Object.keys(dl).forEach(function(k){if(ff.elements[k]&&dl[k])ff.elements[k].value=dl[k]});}}catch(e){}
 if(window.goatcounter)setTimeout(function(){window.goatcounter&&goatcounter.count({path:'ordine-pagato',title:'Ordine pagato',event:true})},1500);
 var c=document.getElementById('sig'),x=c.getContext('2d'),dr=false,has=false;x.lineWidth=4;x.lineCap='round';x.lineJoin='round';x.strokeStyle='#0f1b33';
 function pos(e){var r=c.getBoundingClientRect();return[(e.clientX-r.left)*c.width/r.width,(e.clientY-r.top)*c.height/r.height]}
 c.addEventListener('pointerdown',function(e){dr=true;has=true;c.setPointerCapture(e.pointerId);var p=pos(e);x.beginPath();x.moveTo(p[0],p[1]);e.preventDefault()});
 c.addEventListener('pointermove',function(e){if(!dr)return;var p=pos(e);x.lineTo(p[0],p[1]);x.stroke();e.preventDefault()});
 ['pointerup','pointercancel','pointerleave'].forEach(function(t){c.addEventListener(t,function(){dr=false})});
 window.coClear=function(){x.clearRect(0,0,c.width,c.height);has=false};window.coHas=function(){return has};})();
function coVal(n){var f=document.getElementById('form-lettera');return(f.elements[n]&&f.elements[n].value||'').trim()}
function coDelega(){var d=window.LETTERA,oggi=new Date().toLocaleDateString('it-IT',{day:'numeric',month:'long',year:'numeric'});var nome=coVal('nome'),cf=coVal('cf'),ind=coVal('indirizzo'),cod=coVal('codice'),luogo=coVal('luogo');
 return 'DELEGA ALLA TRASMISSIONE DELLA DISDETTA\n\nIl/La sottoscritto/a '+nome+', codice fiscale '+cf+', residente in '+ind+', intestatario/a del contratto n. '+cod+' con '+d.azienda+',\n\nDELEGA\n\nLouis Lardeux, imprenditore individuale (SIREN 999 443 880, Francia), titolare del servizio DisdettaAbbonamento.it, a trasmettere in suo nome e per suo conto'+(d.pec?', a mezzo posta elettronica certificata all\'indirizzo '+d.pec+',':' a mezzo posta elettronica certificata')+' la comunicazione di disdetta allegata, da lui/lei sottoscritta, e a ricevere le relative ricevute di accettazione e di consegna, che gli/le saranno trasmesse all\'indirizzo '+coVal('email')+'.\n\nLa presente delega è conferita ai sensi degli articoli 1703 e seguenti del Codice civile, è limitata alla sola trasmissione della comunicazione allegata e non comprende alcun altro potere.\n\nSi allega copia del documento d\'identità del delegante.\n\n'+luogo+', '+oggi+'\n\nFirma del delegante'}
function coStep2(){var d=window.LETTERA;if(!d.azienda){d.azienda=coVal('azienda')}genLettera();var l=document.getElementById('lettera');l.style.display='none';document.getElementById('azioni').style.display='none';
 document.getElementById('co-txt-l').textContent=l.textContent;document.getElementById('co-txt-d').textContent=coDelega();
 document.getElementById('co-2').hidden=false;document.querySelectorAll('.co-steps li')[1].className='on';document.getElementById('co-2').scrollIntoView({behavior:'smooth',block:'start'});return false}
function coPdf(){if(!coHas()){document.getElementById('co-err').hidden=false;return}document.getElementById('co-err').hidden=true;
 var J=window.jspdf&&window.jspdf.jsPDF;if(!J){alert('Caricamento in corso, riprova tra un secondo.');return}
 var doc=new J({unit:'mm',format:'a4'}),img=(function(){var c=document.getElementById('sig'),t=document.createElement('canvas');t.width=600;t.height=200;var g=t.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,600,200);g.drawImage(c,0,0,600,200);return t.toDataURL('image/jpeg',.85)})();
 function pagina(txt,firmaLabel){doc.setFont('helvetica','normal');doc.setFontSize(10.5);var lines=doc.splitTextToSize(txt.replace('____________________\n(firma)','').trim(),178),y=20;lines.forEach(function(r){if(y>270){doc.addPage();y=20}doc.text(r,16,y);y+=5});y+=4;if(y>245){doc.addPage();y=20}doc.addImage(img,'JPEG',16,y,60,20);doc.setFontSize(9);doc.text(firmaLabel,16,y+24)}
 pagina(document.getElementById('co-txt-l').textContent,'(firma dell\'intestatario)');doc.addPage();pagina(document.getElementById('co-txt-d').textContent,'(firma del delegante)');
 var nome=coVal('nome').replace(/[^A-Za-z0-9]+/g,'-').replace(/^-|-$/g,'')||'cliente',fn='disdetta-'+nome+'.pdf';doc.save(fn);
 document.getElementById('co-fname').textContent=fn;var up=document.getElementById('co-up'),az=window.LETTERA.azienda;
 if(window.DEPOSITO_URL){var fn2=document.getElementById('co-fname').textContent;up.innerHTML='<ol class="co-up"><li><b>Rinomina</b> la foto del documento con il tuo nome, es. <i>'+fn2.replace('.pdf','-documento.jpg')+'</i>.</li><li>Apri lo spazio di caricamento sicuro e carica <b>il PDF</b> e <b>il documento</b> (fronte e retro).</li></ol><a class="btn shine" href="'+window.DEPOSITO_URL+'" target="_blank" rel="noopener">Carica i documenti →</a><p class="secure">🔒 Spazio di caricamento protetto (Infomaniak, Svizzera): i file arrivano solo a noi. Problemi con il caricamento? <a href="mailto:info@disdettaabbonamento.it?subject='+encodeURIComponent('Documenti disdetta '+az+' - '+coVal('nome'))+'">Inviali per e-mail</a>.</p>';if(window.goatcounter)goatcounter.count({path:'deposito-aperto',title:'Deposito mostrato',event:true});}
 else{var m='mailto:info@disdettaabbonamento.it?subject='+encodeURIComponent('Documenti disdetta '+az+' - '+coVal('nome'))+'&body='+encodeURIComponent('In allegato il PDF firmato (lettera + delega) e il documento d\'identità fronte e retro.\n\nNome: '+coVal('nome')+'\nOperatore: '+az+'\nE-mail per le ricevute: '+coVal('email'));up.innerHTML='<a class="btn shine" href="'+m+'">Invia i documenti per e-mail →</a><p class="secure">Si apre la tua app di posta: allega il PDF appena scaricato e la foto del documento, poi invia.</p>';}
 document.getElementById('co-3').hidden=false;document.querySelectorAll('.co-steps li')[2].className='on';document.getElementById('co-3').scrollIntoView({behavior:'smooth',block:'start'});
 if(window.goatcounter)goatcounter.count({path:'pdf-firmato',title:'PDF firmato',event:true});}
function upsell(){var u=document.getElementById('upsell');if(!u||u.dataset.done)return;u.dataset.done='1';u.hidden=false;requestAnimationFrame(function(){u.classList.add('in')});if(window.goatcounter)goatcounter.count({path:'upsell-mostrato'+location.pathname,title:'Upsell mostrato',event:true});}
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
<div class="plan pro">""" + seal() + """<span class="tag">Consigliato</span><h3>Te la inviamo noi via PEC</h3><div class="price">7,90 € <small>una tantum</small></div><p class="launch"><b>Prezzo di lancio</b> fino al 30 novembre 2026, poi 9,90 €. <span class="cd" data-cd="2026-11-30"></span></p><ul><li>Lettera redatta secondo la legge, con i riferimenti normativi corretti</li><li>Inviata in PEC all'indirizzo verificato dell'operatore</li><li>Ricevuta di consegna con valore legale, inviata alla tua e-mail</li><li>Seguiamo la pratica fino alla conferma: ti inoltriamo ogni risposta dell'operatore</li><li>Non serve avere una PEC né andare in posta</li><li>Rimborso completo se la PEC non viene consegnata</li></ul><a class="btn" href="https://buy.stripe.com/14AcN41JJ3oBcFB1kI2B200?client_reference_id={BRAND_REF}" rel="nofollow" data-pec>Invia via PEC, 7,90 €</a><ul class="tl"><li>🔒 Pagamento sicuro Stripe</li><li>📬 Ricevute PEC entro 2 giorni lavorativi</li><li>🔁 Seguito fino alla conferma</li><li>↩️ Rimborso se la PEC non viene consegnata</li><li>✉️ Una tantum, nessun abbonamento</li></ul><span class="soon">Carta, Apple Pay o Google Pay, pagamento gestito da Stripe. <a href="/termini/">Termini del servizio</a></span><ol class="after"><li><b>Paghi</b> in 30 secondi su Stripe.</li><li><b>Ricevi un'e-mail</b> con il modulo per i dati della lettera, la firma e il documento.</li><li><b>Inviamo la PEC</b> all'indirizzo verificato e ti giriamo le ricevute di accettazione e consegna, entro 2 giorni lavorativi.</li><li><b>Seguiamo la pratica</b>: ogni risposta dell'operatore ti arriva via e-mail, e se chiede un'integrazione ritrasmettiamo senza costi, fino alla conferma.</li></ol></div>
</div>
<div class="rv guar"><div><b>⚖️ Conforme alla legge</b>Testo con le norme del settore: legge Bersani, Codice civile, regole ARERA.</div><div><b>📬 Prova legale</b>La ricevuta PEC ha lo stesso valore di una raccomandata A/R.</div><div><b>🔎 Indirizzi verificati</b>Presi dai documenti ufficiali, con data di verifica.</div><div><b>🔒 Dati protetti</b>Nessun dato salvato per la lettera gratuita, GDPR per l'invio.</div></div>"""


DEMO_TXT = ("Spett.le Sky Italia\nPEC: servizioclientisky@pec.skytv.it\n\nOGGETTO: recesso dal contratto n. 12345678\n\n"
            "Il sottoscritto Mario Rossi, intestatario del contratto,\n\nCOMUNICA\n\nla propria volontà di recedere dal suddetto contratto, "
            "ai sensi dell'art. 1, comma 3, della Legge 40/2007, con effetto dalla scadenza del preavviso.\n\n"
            "CHIEDE la cessazione di ogni addebito e conferma scritta.\n\nDistinti saluti.")


def demo_html(brands):
    d = ('<div class="demo" aria-hidden="true"><div class="float f1">⚡ Lettera pronta in 1 minuto</div><div class="float f2">🔒 Nessun dato salvato</div>'
         '<div class="head"><i></i><i></i><i></i></div><pre id="demo-txt" data-t="' + E(DEMO_TXT) + '"></pre><div class="stamp" id="stamp">PEC consegnata ✓</div></div></section>')
    m = f'<div class="marquee" aria-hidden="true"><div class="track" style="animation-duration:{max(90, len(brands) * 2)}s">' + "".join(f'<span>✓ <b>{E(b["nome"])}</b></span>' for b in brands * 2) + '</div></div>'
    s = ('<div class="tstrip rv"><div><i>🔎</i><span><b>Fonti ufficiali</b>Ogni indirizzo con fonte e data</span></div>'
         '<div><i>⚖️</i><span><b>Lettera a norma</b>Bersani, Codice civile, ARERA</span></div>'
         '<div><i>📬</i><span><b>Prova legale</b>Ricevuta PEC come una A/R</span></div>'
         '<div><i>🔒</i><span><b>Privacy</b>Nessun dato salvato</span></div></div>')
    return d + m + s


REVIEWS = ('<h2>Le recensioni</h2><div class="reviews rv"><div class="rev"><div class="st">★★★★★</div><p>Il servizio è appena nato: qui pubblicheremo solo recensioni vere dei primi utenti.</p></div>'
           '<div class="rev"><div class="st">★★★★★</div><p>Hai usato una lettera o l\'invio PEC? Raccontaci com\'è andata a <a href="mailto:info@disdettaabbonamento.it">info@disdettaabbonamento.it</a>.</p></div>'
           '<div class="rev"><div class="st">★★★★★</div><p>Ogni recensione viene pubblicata con nome e data, senza filtri.</p></div></div>')


TERMINI_HTML = r'''<h1>Termini e condizioni del servizio</h1>
<p class="src">Versione del 31 ottobre 2026.</p>
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
<p>L'invio avviene di norma entro 2 giorni lavorativi dal ricevimento dei documenti completi (lettera firmata, delega firmata, documento d'identità). Le ricevute PEC di accettazione e di consegna sono inoltrate all'indirizzo e-mail indicato dal cliente non appena disponibili. La ricevuta di consegna attesta che il messaggio è stato consegnato nella casella PEC del destinatario e costituisce prova dell'invio e della data.</p>
<p><strong>Seguito fino alla conferma.</strong> Le risposte dell'operatore arrivano alla nostra casella PEC. Per 90 giorni dall'invio inoltriamo al cliente ogni risposta ricevuta, entro 2 giorni lavorativi. Se l'operatore chiede un'integrazione (un dato mancante, un modulo proprio, una nuova firma), lo comunichiamo al cliente e, una volta ricevuto quanto richiesto, ritrasmettiamo la disdetta senza costi aggiuntivi. Il seguito termina con la conferma della cessazione da parte dell'operatore, o al più tardi dopo 90 giorni.</p>
<h2>6. Cosa non possiamo garantire</h2>
<p>Il nostro impegno riguarda la corretta trasmissione della disdetta e il seguito descritto sopra; l'esito della disdetta dipende dal contratto e dall'operatore. In particolare non siamo responsabili delle decisioni dell'operatore, dei tempi con cui gestisce la disdetta, di eventuali costi o penali previsti dal contratto del cliente, di una disdetta tardiva rispetto al preavviso contrattuale quando il cliente completa l'ordine o i documenti dopo il termine utile, né delle conseguenze di dati incompleti o errati forniti dal cliente. Se l'operatore accetta la disdetta solo con modalità che non possiamo eseguire per conto del cliente (firma digitale del titolare, invio dalla sua casella PEC personale, presenza in negozio), lo comunichiamo al cliente con le istruzioni per procedere e rimborsiamo l'importo se la PEC non è ancora stata inviata. Le schede informative sono verificate sulle fonti indicate alla data riportata, ma le condizioni degli operatori possono cambiare: in caso di dubbio fa fede il contratto del cliente. Il servizio non costituisce consulenza legale.</p>
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
<h2>Statistiche di navigazione</h2>
<p>Per contare le visite usiamo GoatCounter, uno strumento che non utilizza cookie, non memorizza l'indirizzo IP né identificatori personali e non traccia l'utente tra siti diversi. Raccoglie solo dati aggregati (pagina visitata, Paese, tipo di dispositivo, sito di provenienza). Per questo non è richiesto alcun consenso. Informazioni: <a href="https://www.goatcounter.com/help/privacy" rel="noopener nofollow">goatcounter.com/help/privacy</a>.</p>
<h2>Cookie</h2>
<p>Il sito non utilizza cookie di profilazione. Eventuali strumenti tecnici necessari al funzionamento non richiedono consenso.</p>'''



TALLY_URL = ""  # (non utilisé)
DEPOSITO_URL = "https://kdrive.infomaniak.com/app/collaborate/3448442/a57dbb0a-6e5e-4c31-bf7b-1f05bdf571e1"  # boîte de dépôt kDrive Infomaniak, dossier « Disdetta - documenti clienti »

COMPLETA_HTML = """<section class="hero small"><span class="pill"><b>✓</b> Pagamento ricevuto</span>
<h1>Grazie! Completa il tuo ordine <em>in 3 minuti</em></h1>
<p class="lead">Per inviare la disdetta in PEC al posto tuo ci servono la lettera firmata, la delega firmata e una copia del tuo documento d'identità. Le prepariamo qui sotto con i tuoi dati: tu firmi con il dito o il mouse.</p>
<ol class="co-steps"><li class="on"><b>1</b> I tuoi dati</li><li><b>2</b> Firma</li><li><b>3</b> Invia i documenti</li></ol></section>
<section class="gen" id="co-1"><h2>1. I tuoi dati</h2>
<p class="sub" id="co-op"></p>
<form id="form-lettera" onsubmit="return coStep2()">
<div id="co-opfield" hidden><label for="co-azienda">Operatore da disdire</label><input id="co-azienda" name="azienda" placeholder="es. Sky, TIM, Generali"></div>
<div class="row2"><div><label for="nome">Nome e cognome dell'intestatario</label><input id="nome" name="nome" autocomplete="name" required></div>
<div><label for="cf">Codice fiscale</label><input id="cf" name="cf" required></div></div>
<label for="indirizzo">Indirizzo di residenza</label><input id="indirizzo" name="indirizzo" autocomplete="street-address" required>
<div class="row2"><div><label for="codice">Codice cliente, numero di contratto o di polizza</label><input id="codice" name="codice" required></div>
<div><label for="linea">Numero di telefono o POD/PDR collegato (facoltativo)</label><input id="linea" name="linea"></div></div>
<div class="row2"><div><label for="luogo">Città</label><input id="luogo" name="luogo" autocomplete="address-level2" required></div><div><label for="email">La tua e-mail (per ricevere le ricevute PEC)</label><input id="email" name="email" type="email" autocomplete="email" required></div></div>
<label class="chk"><input type="checkbox" id="co-ok" required> Dichiaro di essere l'intestatario del contratto, o di essere autorizzato ad agire per suo conto, e che i dati sono veritieri.</label>
<button class="btn" type="submit">Continua alla firma →</button><p class="secure">🔒 I dati restano nel tuo browser finché non invii i documenti.</p></form>
<div id="lettera" hidden></div><div id="azioni" hidden></div></section>
<section class="gen" id="co-2" hidden><h2>2. Firma</h2>
<p class="sub">Firma nel riquadro con il dito o con il mouse. La stessa firma viene apposta sulla lettera di disdetta e sulla delega.</p>
<div class="sig"><canvas id="sig" width="900" height="300" aria-label="Riquadro per la firma"></canvas><button type="button" class="btn sec" onclick="coClear()">Cancella</button></div>
<details class="co-prev"><summary>Leggi la lettera e la delega prima di firmare</summary><pre id="co-txt-l"></pre><pre id="co-txt-d"></pre></details>
<button class="btn shine" type="button" onclick="coPdf()">Firma e scarica il PDF →</button><p class="co-err" id="co-err" hidden>Firma nel riquadro prima di continuare.</p></section>
<section class="gen" id="co-3" hidden><h2>3. Invia i documenti</h2>
<p class="sub">Il PDF <b id="co-fname"></b> è stato scaricato sul tuo dispositivo. Ora invia due cose:</p>
<ul class="co-list"><li>📄 il PDF firmato (lettera + delega)</li><li>🪪 una foto o scansione del documento d'identità, fronte e retro</li></ul>
<div id="co-up"></div>
<p class="co-after">Riceverai le ricevute PEC di accettazione e di consegna nella tua e-mail entro 2 giorni lavorativi dal ricevimento dei documenti. Poi seguiamo la pratica: ogni risposta dell'operatore ti viene inoltrata, fino alla conferma della cessazione. Problemi? Scrivi a <a href="mailto:info@disdettaabbonamento.it">info@disdettaabbonamento.it</a>.</p></section>"""

def page(title, desc, path, body, schema=None, sticky="", noindex=False, extra_head=""):
    canon = DOMAIN + path
    bodycls = ' class="has-sticky"' if sticky else ""
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in (schema or []))
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">{'<meta name="robots" content="noindex,nofollow">' if noindex else ''}{extra_head}
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canon}"><meta property="og:locale" content="it_IT">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta property="og:image" content="https://disdettaabbonamento.it/og.png"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="/style.css?v={ASSET_V}">{ld}</head><body{bodycls}>
<div class="trustbar" aria-label="Garanzie del servizio"><div class="tb-track"><span>🔒 Pagamento sicuro con Stripe</span><span>💳 Carta, PayPal, Satispay, Apple Pay e Klarna</span><span>📬 Invio PEC entro 2 giorni lavorativi</span><span>⚖️ La PEC vale come una raccomandata A/R</span><span>🔎 Indirizzi verificati sulle fonti ufficiali</span><span>↩️ Rimborso se la PEC non viene consegnata</span><span>✉️ Una tantum, nessun abbonamento</span><span>🏷️ 7,90 €: il prezzo più basso tra i servizi di disdetta via PEC</span><span>💬 Rispondiamo via e-mail entro 24 ore, 7 giorni su 7</span><span aria-hidden="true">🔒 Pagamento sicuro con Stripe</span><span aria-hidden="true">💳 Carta, PayPal, Satispay, Apple Pay e Klarna</span><span aria-hidden="true">📬 Invio PEC entro 2 giorni lavorativi</span><span aria-hidden="true">⚖️ La PEC vale come una raccomandata A/R</span><span aria-hidden="true">🔎 Indirizzi verificati sulle fonti ufficiali</span><span aria-hidden="true">↩️ Rimborso se la PEC non viene consegnata</span><span aria-hidden="true">✉️ Una tantum, nessun abbonamento</span><span aria-hidden="true">🏷️ 7,90 €: il prezzo più basso tra i servizi di disdetta via PEC</span><span aria-hidden="true">💬 Rispondiamo via e-mail entro 24 ore, 7 giorni su 7</span></div></div>
<header class="top"><div class="wrap"><a class="logo" href="/"><i>✉</i><span class="lt">Disdetta<span>Abbonamento</span>.it</span></a>
<nav class="main"><a href="/telefonia/">Telefonia</a><a href="/luce-gas/">Luce e gas</a><a href="/assicurazioni/">Assicurazioni</a><a href="/guide/">Guide</a><a class="cta" href="/#cerca"><span class="lg">Trova il tuo operatore</span><span class="sm">Cerca</span></a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap"><p><a href="/">Home</a><a href="/guide/">Guide</a><a href="/come-funziona/">Come funziona</a><a href="/chi-siamo/">Chi siamo</a><a href="/note-legali/">Note legali</a><a href="/termini/">Termini e condizioni</a><a href="/privacy/">Privacy</a></p>
<p>{SITE} è un servizio indipendente, non affiliato agli operatori citati. I marchi appartengono ai rispettivi proprietari. Le informazioni sono verificate sulle fonti ufficiali alla data indicata in ogni pagina: controlla sempre il tuo contratto.</p></div></footer>
{sticky}<script src="/app.js?v={ASSET_V}" defer></script><script data-goatcounter="https://disdetta.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script></body></html>"""


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
    if b["categoria"] == "assicurazioni" and b.get("pec"):
        corto = re.sub(r"\s*\(.*?\)", "", n)
        title = f"PEC {corto} per disdetta: indirizzo e lettera ({anno})"
    desc = (f"Come disdire {n}: indirizzo PEC, raccomandata, preavviso e costi verificati sulle fonti ufficiali. Genera gratis la lettera di disdetta pronta da inviare."
            if lettera else f"Come annullare l'abbonamento {n} in pochi passaggi, senza lettere. Preavviso, costi e cosa succede dopo, verificato sulle fonti ufficiali.")
    if b["categoria"] == "assicurazioni" and b.get("pec"):
        desc = f"Indirizzo PEC {n} per la disdetta della polizza, verificato sulle fonti ufficiali. Calcola entro quando inviarla e genera gratis la lettera pronta."
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
    ref = re.sub(r"[^A-Za-z0-9_-]+", "-", n).strip("-")[:60]
    sl = E(b["slug"])
    stripe = "https://buy.stripe.com/14AcN41JJ3oBcFB1kI2B200?client_reference_id=" + ref + ""
    _can = " ".join(b.get("canali", [])).lower()
    facile = ("pulsante di disdetta online: sì" in _can) or ("online (" in _can) or ("e-mail ordinaria" in _can)
    assic = b["categoria"] == "assicurazioni"
    body = '<section class="hero small">'
    body += f'<p class="crumbs"><a href="/">Home</a> › <a href="/{cat["slug"]}/">{E(cat["nome"])}</a> › {E(n)}</p>'
    body += f'<span class="pill">{"<b>✓</b> Verificato su fonte ufficiale" if uff else "Verificato su fonti di settore"} · {verif}</span>'
    body += f"<h1>Disdetta {E(n)}: <em>{'PEC, indirizzo e lettera pronta' if lettera else 'come annullare in pochi clic'}</em></h1>"
    body += (f'<p class="lead">Dove inviare la disdetta, con quale preavviso e quanto costa. La inviamo noi via PEC con ricevuta legale in 3 minuti, oppure prepari tu la lettera gratis.</p>'
             if lettera else f'<p class="lead">{E(n)} si disdice online, senza lettere. Ecco i passaggi, il preavviso e cosa succede dopo.</p>')
    # Bloc réponse directe, lisible d'un coup d'œil par Google, les IA et l'appelant pressé
    parti = []
    if b.get("pec"): parti.append(f"PEC <strong class=\"pec\">{E(b['pec'])}</strong>")
    if b.get("indirizzo_postale"): parti.append(f"raccomandata A/R a <strong>{E(b['indirizzo_postale'])}</strong>")
    if b.get("preavviso"): parti.append(f"preavviso <strong>{E(b['preavviso'])}</strong>")
    if b.get("costi"): parti.append(f"costi: {E(b['costi'])}")
    if not parti and b.get("canali"): parti.append("si disdice direttamente da " + ", ".join(E(c) for c in b["canali"][:3]))
    if parti:
        body += f'<p class="inbreve"><b>In breve.</b> Per disdire {E(n)}: ' + "; ".join(parti) + f'. Verificato il {verif} su {"fonte ufficiale" if uff else "fonti di settore"}.</p>'
    if lettera:
        body += f'<a class="btn shine" href="{stripe}" rel="nofollow" data-pec>Te la inviamo noi via PEC, 7,90 € →</a><a class="btn sec" href="#lettera-disdetta">Preferisco la lettera gratis</a>'
    body += '<ul class="chips"><li>Senza PEC, senza posta</li><li>Ricevuta con valore legale nella tua e-mail</li><li>Rimborso se non consegnata</li><li>Lettera gratis se preferisci</li></ul><p class="proof" data-proof="' + sl + '" hidden></p></section>'
    if b.get("pec"):
        facts[0] = ("PEC", f'<span class="pec">{E(b["pec"])}</span> <button class="copy" type="button" onclick="copiaPec(this,\'{E(b["pec"])}\')">Copia</button>')
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
    body += f'<div class="rv box" id="dati"><h2>Disdetta {E(n)} in breve</h2><dl class="facts">{dl}</dl></div>'
    gg = re.search(r"(\d+)\s*giorni", b.get("preavviso", "") or "")
    if lettera and gg and assic:
        body += (f'<div class="urg rv urg-ass"><span class="ic">⏰</span><span><b>Quando scade la tua polizza?</b><p>Per non farla rinnovare, la disdetta deve arrivare a {E(n)} almeno {gg.group(1)} giorni prima della scadenza. Dopo quella data la polizza può rinnovarsi per un altro anno.</p>'
                 f'<form class="dl" onsubmit="return calcScad(this,{gg.group(1)})"><label for="dl-{sl}">Inserisci la data di scadenza della polizza (la trovi sul contratto o sull\'avviso di scadenza)</label><div class="dlrow"><input type="date" id="dl-{sl}" name="d" required><button class="btn sec" type="submit">Calcola</button></div><p class="dlout" aria-live="polite"></p></form></span>'
                 f'<div class="urgbtns"><a class="btn shine" href="{stripe}" rel="nofollow" data-pec>Inviala oggi via PEC, 7,90 €</a><a class="btn sec" href="#lettera-disdetta">Lettera gratis</a></div></div>')
    elif lettera and gg:
        body += f'<div class="urg rv"><span class="ic">⏰</span><span><b>Se invii oggi, il contratto termina il <span id="scad" data-giorni="{gg.group(1)}">…</span></b><p>Con {gg.group(1)} giorni di preavviso ogni giorno di attesa sposta la fine del contratto. Aspettare una settimana vuol dire pagare fino al <span id="scad2">…</span>, spesso un mese in più.</p><form class="dl" onsubmit="return calcScad(this,{gg.group(1)})"><label for="dl-{sl}">Hai una scadenza precisa? Inserisci la data di scadenza o di rinnovo del contratto</label><div class="dlrow"><input type="date" id="dl-{sl}" name="d" required><button class="btn sec" type="submit">Calcola</button></div><p class="dlout" aria-live="polite"></p></form></span><div class="urgbtns"><a class="btn shine" href="{stripe}" rel="nofollow" data-pec>Disdici oggi via PEC, 7,90 €</a><a class="btn sec" href="#lettera-disdetta">Lettera gratis</a></div></div>'

    ap = APPROF.get(b["slug"])
    if ap and ap.get("testo"):
        body += f'<h2>Cosa sapere su {E(n)}</h2><p class="approf">{E(ap["testo"])}</p>'
    if b.get("note"):
        body += f'<div class="note"><strong>Da sapere.</strong> {E(b["note"])}</div>'
    if lettera:
        body += f'<h2>Come disdire {E(n)} in 3 passaggi</h2><div class="rv steps"><div class="step"><div class="n">1</div><h3>Compila la lettera</h3><p>Nome, indirizzo e codice cliente: la lettera si genera qui sotto.</p></div><div class="step"><div class="n">2</div><h3>Firma e allega il documento</h3><p>Aggiungi la firma e una copia del documento d\'identità.</p></div><div class="step"><div class="n">3</div><h3>Invia {"via PEC" if b.get("pec") else "con raccomandata A/R"}</h3><p>All\'indirizzo indicato sopra. Conserva la ricevuta: è la prova della data.</p></div></div>'
    body += f"<h2>Tutti i canali per disdire {E(n)}</h2><ul class=\"canali\">{canali}</ul>"
    if lettera:
        body += f'<div class="ctabar rv"><span><b>Vuoi che ce ne occupiamo noi?</b> Lettera a norma, PEC all\'indirizzo verificato, ricevute nella tua e-mail. Prezzo di lancio 7,90 €.</span><a class="btn" href="{stripe}" rel="nofollow" data-pec>Invia via PEC →</a></div>'
    if lettera:
        via = "PEC" if b.get("pec") else "raccomandata A/R"
        scelta = ""
        if b.get("pec"):
            domanda = (f'<b>Puoi disdire {E(n)} anche dai suoi canali online</b>, ma solo la PEC o la raccomandata ti lasciano una prova con valore legale della data, utile se la disdetta viene contestata o ti arrivano altri addebiti. Come preferisci procedere?'
                       if facile else f'<b>Per disdire {E(n)} con una prova della data serve una PEC</b> oppure una raccomandata A/R in posta. Come preferisci procedere?')
            tag = "La prova più sicura" if facile else "Consigliato se non hai una PEC"
            scelta = (f'<div class="scelta" id="scelta"><p class="sc-q">{domanda}</p><div class="sc-grid">'
                f'<div class="sc pro"><span class="tag">{tag}</span><h3>Te la inviamo noi via PEC</h3><div class="price">7,90 € <small>una tantum</small></div><ul><li>✓ Non serve avere una PEC né andare in posta</li><li>✓ Ricevuta con valore legale nella tua e-mail: la prova della data</li><li>✓ Seguiamo la pratica fino alla conferma di {E(n)}</li></ul><a class="btn shine" href="{stripe}" rel="nofollow" data-pec>Invia via PEC, 7,90 € →</a><small>🔒 Pagamento Stripe · ↩️ Rimborso se non consegnata</small></div>'
                f'<div class="sc"><h3>La invio da solo</h3><div class="price">Gratis</div><ul><li>Lettera pronta qui sotto, da copiare o stampare</li><li>Serve la tua PEC personale, oppure una raccomandata A/R allo sportello (circa 6-7 €)</li><li>Le risposte dell\'operatore le segui tu</li></ul><a class="btn sec" href="#form-lettera" onclick="if(window.goatcounter)goatcounter.count({{path:\'scelta-gratis\'+location.pathname,title:\'Scelta lettera gratis\',event:true}})">Genera la lettera gratis ↓</a></div>'
                '</div></div>')
        body += f"""<section class="gen" id="lettera-disdetta"><h2>Lettera di disdetta {E(n)}, gratis</h2>
{scelta}
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
<div id="azioni" class="noprint" style="display:none"><div class="upsell" id="upsell" hidden><b>La tua lettera è pronta. Ultimo passo: inviarla.</b><p style="margin:6px 0 10px">Hai già inserito tutto: i tuoi dati passano direttamente all'ordine, e in 3 minuti la disdetta parte via PEC all'indirizzo verificato di {E(n)}.</p><table><tr><th></th><th>Da solo</th><th>Con noi</th></tr><tr><td>Senza PEC</td><td>Stampa, firma, raccomandata A/R in posta: circa 6-7 € e la fila allo sportello</td><td>✓ Non serve</td></tr><tr><td>Prova della data</td><td>Ricevuta cartacea da conservare</td><td>✓ Ricevute PEC nella tua e-mail</td></tr><tr><td>Risposte dell'operatore</td><td>Le segui tu</td><td>✓ Le seguiamo noi fino alla conferma</td></tr><tr><td>Tempo</td><td>Mezza giornata</td><td>✓ 3 minuti, da casa</td></tr></table><p class="urgente">⏰ Ogni giorno di attesa sposta la fine del contratto. Con la PEC la data di invio fa fede da oggi; una raccomandata può impiegare diversi giorni per arrivare.</p><p class="legale">⚖️ <b class="inl">Valore legale:</b> la PEC equivale per legge alla raccomandata con ricevuta di ritorno (<a href="https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2005-03-07;82~art48" target="_blank" rel="noopener">art. 48 del Codice dell'amministrazione digitale</a>). Le ricevute di accettazione e di avvenuta consegna provano data e contenuto dell'invio.</p><ol class="passi"><li><strong>Paghi 7,90 €</strong> in modo sicuro</li><li><strong>Firmi online</strong> e alleghi il documento</li><li><strong>Ricevi le ricevute PEC</strong> di accettazione e consegna nella tua e-mail</li></ol><a class="btn shine" href="{stripe}" rel="nofollow" data-pec>Inviala ora via PEC, 7,90 € →</a><ul class="tl"><li>🔒 Pagamento sicuro Stripe: non vediamo i dati della tua carta</li><li>📬 Ricevute PEC entro 2 giorni lavorativi</li><li>🔁 Seguito fino alla conferma</li><li>↩️ Rimborso se la PEC non viene consegnata</li><li>✉️ Una tantum, nessun abbonamento</li></ul><p class="launch" style="margin-top:10px">Prezzo di lancio 7,90 € fino al 30 novembre 2026, poi 9,90 €.</p><p class="legale" style="margin-top:6px">🏷️ Il prezzo più basso tra i servizi di invio disdetta via PEC: gli altri partono da 9,95 € (verifica novembre 2026).</p><div class="founder mini"><img src="/louis.jpg" alt="Louis Lardeux" width="48" height="64"><div><b>Louis Lardeux, fondatore</b><span>Domande prima di ordinare? Scrivimi a <a href="mailto:info@disdettaabbonamento.it">info@disdettaabbonamento.it</a>, rispondo entro 24 ore, 7 giorni su 7. <a href="/chi-siamo/">Chi siamo</a></span></div></div></div><p style="margin:16px 0 6px;font-weight:600">Preferisci inviarla da solo?</p><button class="btn sec" type="button" onclick="copiaLettera(this);upsell()">Copia il testo</button><button class="btn sec" type="button" onclick="upsell();window.print()">Salva in PDF / stampa</button>
<p class="src">Per una disdetta con valore legale, invia la lettera firmata con copia del documento d'identità da una casella PEC, oppure con raccomandata A/R, e conserva la ricevuta.</p>
<div class="pecbox"><div><b>Non hai una PEC?</b><span>La inviamo noi all'indirizzo verificato di {E(n)}, con ricevuta di consegna a valore legale nella tua e-mail, e seguiamo la pratica fino alla conferma. Prezzo di lancio 7,90 € fino al 30 novembre, poi 9,90 €.</span></div><a class="btn shine" href="{stripe}" rel="nofollow" data-pec>Invia via PEC, 7,90 € →</a><ul class="tl"><li>🔒 Pagamento sicuro Stripe</li><li>📬 Ricevute PEC entro 2 giorni lavorativi</li><li>🔁 Seguito fino alla conferma</li><li>↩️ Rimborso se la PEC non viene consegnata</li><li>✉️ Una tantum, nessun abbonamento</li></ul></div></div>
<script>window.LETTERA={json.dumps({"azienda": n, "pec": b.get("pec", ""), "postale": b.get("indirizzo_postale", "") or ("[indirizzo del tuo club, indicato nel contratto]" if b["categoria"] == "palestre" else ""), "servizio": cat["servizio"], "legge": LEGGE_BREVE.get(b["categoria"], ""), "campo": CAMPO[b["categoria"]], "cat": b["categoria"]}, ensure_ascii=False)}</script>
</section>"""
    if lettera:
        body += PLANS.replace("{BRAND_REF}", ref)
    rel = [g for g in GUIDE if b["categoria"] in g["cats"]][:3]
    if rel:
        body += '<h2>Guide utili</h2><div class="grid">' + "".join(f'<a class="card" href="/guide/{g["slug"]}/"><span class="av altri-servizi">📘</span><span><b>{E(g["h1"])}</b><small>Guida</small></span></a>' for g in rel) + '</div>'
    body += f"<h2>Cosa dice la legge</h2><p>{E(cat['legge'])}</p>"
    if lettera:
        body += f'<div class="ctabar rv alt"><span><b>Hai letto abbastanza?</b> Genera la lettera gratis in un minuto, oppure facciamo tutto noi via PEC.</span><span class="ctab"><a class="btn" href="{stripe}" rel="nofollow" data-pec>Invia via PEC, 7,90 €</a><a class="btn sec" href="#lettera-disdetta">Lettera gratis</a></span></div>'
    faqs = faq_brand(b, cat)
    if faqs:
        body += "<h2>Domande frequenti</h2>" + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faqs)
    if peers:
        body += f"<h2>Altre disdette: {E(cat['nome'].lower())}</h2><div class=\"grid\">" + "".join(
            card(p) for p in peers) + "</div>"
    host = lambda u: re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
    _seen = {}
    for u in b.get("fonti", []) + APPROF.get(b["slug"], {}).get("fonti", []):
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
        body += f'<section class="band"><h2>Disdici {E(n)} oggi</h2><p>Te la inviamo noi in PEC con ricevuta legale, in 3 minuti da casa. Oppure prepari la lettera gratis.</p><a class="btn shine" href="{stripe}" rel="nofollow" data-pec>Te la inviamo noi, 7,90 € →</a><a class="btn sec" href="#lettera-disdetta">Lettera gratis</a></section>'
    sticky = f'<aside class="slidein" id="slidein" hidden><button class="x" type="button" aria-label="Chiudi" onclick="chiudiSlide()">×</button><b>Non hai una PEC?</b><p>Inviamo noi la disdetta a {E(n)} con ricevuta legale. Prezzo di lancio 7,90 € fino al 30 novembre.</p><a class="btn" href="{stripe}" rel="nofollow" data-pec>Invia via PEC →</a><small>↩️ Rimborso se non consegnata · 🔒 Stripe</small></aside><div class="sticky two"><a class="btn" href="{stripe}" rel="nofollow" data-pec>Invia via PEC, 7,90 €</a><a class="btn sec" href="#lettera-disdetta">Lettera gratis</a></div>' if lettera else ''
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
    global ASSET_V
    import hashlib
    ASSET_V = hashlib.md5((CSS + JS).encode()).hexdigest()[:8]
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
    body += f'<div class="stats"><div><b data-count="{len(brands)}">{len(brands)}</b><span>operatori</span></div><div><b data-count="{nuff}">{nuff}</b><span>schede da fonte ufficiale</span></div><div><b>1 min</b><span>per la lettera</span></div><div><b>7,90 €</b><span>invio PEC per te</span></div></div>' + '<div class="hero-seal">' + seal() + '<p><b>Ricevuta di consegna con valore legale</b>La PEC vale come una raccomandata A/R: la ricevuta prova la data della tua disdetta.</p></div></div>' + demo_html(brands)
    body += '<h2>Come funziona</h2><div class="rv steps"><div class="step"><div class="n">1</div><h3>Cerca l\'operatore</h3><p>Trovi PEC, indirizzo per la raccomandata, preavviso e costi, con la data di verifica.</p></div><div class="step"><div class="n">2</div><h3>Compila la lettera</h3><p>Inserisci i tuoi dati: la lettera di disdetta si genera subito, con i riferimenti di legge.</p></div><div class="step"><div class="n">3</div><h3>Inviala e conserva la ricevuta</h3><p>Via PEC o raccomandata A/R. La ricevuta di consegna è la prova della disdetta.</p></div></div><p style="text-align:center"><a class="btn shine" href="#cerca">Inizia ora, è gratis →</a></p>'
    ICONE = {"telefonia": "📶", "tv-streaming": "📺", "energia": "💡", "assicurazioni": "🛡️", "palestre": "🏋️", "altri-servizi": "🧾"}
    body += '<section class="pricechart rv" aria-label="Confronto dei costi per disdire"><div class="pc-head"><h2>Quanto costa disdire un contratto</h2><p>Il prezzo più basso tra i servizi che inviano la disdetta via PEC al posto tuo.</p></div><div class="pc-row muted"><div class="pc-lab"><b>Raccomandata A/R allo sportello</b><small>+ stampa, firma, fila, consegna in più giorni</small></div><div class="pc-bar"><span style="--w:61.9%"></span><em>circa 6-7 €</em></div></div><div class="pc-row muted"><div class="pc-lab"><b>Altri servizi che inviano la PEC per te</b><small>prezzi pubblici rilevati a novembre 2026</small></div><div class="pc-bar"><span style="--w:94.8%"></span><em>da 9,95 €</em></div></div><div class="pc-row acc"><div class="pc-lab"><b>Disdetta Abbonamento, invio PEC per te <span class="pc-badge">il più conveniente</span></b><small>da casa in 3 minuti, ricevute nella tua e-mail</small></div><div class="pc-bar"><span style="--w:75.2%"></span><em>7,90 €</em></div></div><p class="pc-note">La raccomandata costa un po\' meno, ma la prepari tu, la porti allo sportello e la consegna richiede diversi giorni. La PEC arriva in pochi minuti e vale come una raccomandata A/R.</p></section>'
    body += '<h2>Scegli la categoria</h2><div class="rv cats">' + "".join(f'<a class="cat" href="/{CATEGORIE[c]["slug"]}/"><div class="ic">{ICONE[c]}</div><h3>{E(CATEGORIE[c]["nome"])}</h3><small>{len(bycat[c])} operatori</small></a>' for c in CATEGORIE if c in bycat) + '</div>'
    body += '<div id="operatori">'
    for c in CATEGORIE:
        if c in bycat:
            cat = CATEGORIE[c]
            body += f'<h2><a href="/{cat["slug"]}/" style="color:inherit;text-decoration:none">{E(cat["nome"])}</a></h2><div class="grid">' + "".join(card(b) for b in bycat[c]) + "</div>"
    body += '</div>'
    body += '<h2>Perché usare Disdetta Abbonamento</h2><div class="rv trust"><div><h3>🔎 Indirizzi verificati</h3><p>Ogni PEC e indirizzo viene dai documenti dell\'operatore, con fonte e data di verifica in ogni scheda.</p></div><div><h3>⚖️ Lettera con valore legale</h3><p>Il testo cita le norme giuste (come la legge Bersani per la telefonia) e chiede lo stop di ogni addebito.</p></div><div><h3>🔒 Privacy totale</h3><p>La lettera si genera nel tuo browser. Non chiediamo registrazione e non salviamo i tuoi dati.</p></div></div>'
    body += '<h2>Le nostre guide</h2><div class="grid rv">' + ''.join(gcards[:6]) + '</div><p><a href="/guide/">Tutte le guide →</a></p>'
    body += ('<h2>Perché fidarsi di questo sito</h2><div class="rv guar home"><div><b>👤 Chi c\'è dietro</b>Un servizio indipendente, con nome, partita e contatti pubblicati nelle <a href="/note-legali/">note legali</a>. Nessun legame con gli operatori.</div>'
             '<div><b>🔎 Ogni scheda è verificata</b>Indirizzi PEC, preavvisi e costi presi dai documenti ufficiali, con la data di verifica e le fonti citate in fondo a ogni pagina.</div>'
             '<div><b>↩️ Rimborso garantito</b>Se la PEC non viene consegnata all\'operatore, rimborsiamo l\'intero importo. Le ricevute arrivano nella tua e-mail entro 2 giorni lavorativi.</div>'
             '<div><b>🔒 I tuoi dati restano tuoi</b>La lettera gratuita si genera nel tuo browser, senza invio né salvataggio. Il pagamento passa solo da Stripe. Nessun cookie di profilazione.</div></div>')
    body += '<section class="band"><h2>Pronto a disdire?</h2><p>Cerca il tuo operatore e prepara la lettera adesso, è gratis.</p><a class="btn shine" href="#cerca">Trova il tuo operatore →</a></section>'
    write("/", page("Disdetta abbonamento: PEC, indirizzi e lettere di disdetta gratis",
                    f"Indirizzi PEC e postali verificati, preavviso, costi e lettere di disdetta gratuite per {len(brands)} operatori: telefonia, pay TV, luce e gas, assicurazioni, palestre.", "/", body,
                    [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": DOMAIN + "/"}]))
    # pagine istituzionali
    statiche = {
        "/come-funziona/": ("Come funziona", "Come disdire un contratto con valore legale: PEC o raccomandata A/R, documento d'identità, ricevuta da conservare.",
            "<h1>Come disdire un contratto, passo per passo</h1><ol><li><strong>Trova l'operatore</strong> e controlla preavviso e costi nella sua scheda.</li><li><strong>Compila la lettera</strong>: nome dell'intestatario, indirizzo, codice cliente o numero di contratto.</li><li><strong>Firma la lettera</strong> e allega una copia del documento d'identità.</li><li><strong>Inviala</strong> via PEC dalla tua casella PEC, oppure con raccomandata A/R all'indirizzo indicato.</li><li><strong>Conserva la ricevuta</strong> di consegna: è la prova della data della disdetta.</li></ol><h2>PEC o raccomandata?</h2><p>La PEC ha lo stesso valore legale della raccomandata con ricevuta di ritorno, costa meno ed è immediata. Alcuni operatori accettano solo PEC inviate da un'altra casella PEC, non da un'e-mail normale.</p>"),
        "/chi-siamo/": ("Chi siamo", "Disdetta Abbonamento è un servizio indipendente che raccoglie gli indirizzi ufficiali per disdire i contratti.",
            "<h1>Chi siamo</h1><div class='founder'><img src='/louis.jpg' alt='Louis Lardeux, fondatore di Disdetta Abbonamento' width='120' height='160' loading='lazy'><div><b>Louis Lardeux</b><span>Fondatore di DisdettaAbbonamento.it</span><p>Ho creato questo servizio perché disdire un contratto in Italia è ancora troppo complicato: indirizzi PEC difficili da trovare, preavvisi diversi per ogni operatore, raccomandate da spedire allo sportello.</p></div></div><p>Disdetta Abbonamento è un servizio indipendente, non collegato a nessun operatore. Raccogliamo dai documenti ufficiali degli operatori gli indirizzi PEC e postali, i preavvisi e i costi di disdetta, e li aggiorniamo con la data di verifica in ogni scheda.</p><h2>Come lavoriamo</h2><ul><li>Ogni indirizzo è preso dai documenti ufficiali dell'operatore, con la fonte citata in fondo alla scheda.</li><li>La lettera gratuita si genera sul tuo dispositivo: i tuoi dati non ci arrivano.</li><li>Quando ci affidi l'invio, ti giriamo le ricevute PEC e seguiamo la pratica fino alla conferma.</li></ul><h2>Contatti</h2><p>Scrivici a <a href='mailto:info@disdettaabbonamento.it'>info@disdettaabbonamento.it</a>: rispondiamo entro 24 ore, 7 giorni su 7. Hai trovato un dato non aggiornato? Segnalacelo: verifichiamo e correggiamo.</p>"),

        "/note-legali/": ("Note legali", "Note legali di Disdetta Abbonamento.",
            "<h1>Note legali</h1><h2>Editore del sito</h2><p>Louis Lardeux, imprenditore individuale (micro-entreprise di diritto francese), SIREN 999 443 880, Francia. Contatto: <a href='mailto:info@disdettaabbonamento.it'>info@disdettaabbonamento.it</a>.</p><h2>Informazioni</h2><p>Le informazioni pubblicate hanno scopo informativo e sono verificate sulle fonti ufficiali alla data indicata in ogni scheda. Non costituiscono consulenza legale. In caso di dubbio fa fede il contratto sottoscritto con l'operatore.</p><p>I marchi citati appartengono ai rispettivi titolari e sono usati solo per identificare i servizi.</p>"),
        "/privacy/": ("Privacy", "Informativa privacy di Disdetta Abbonamento: quali dati trattiamo, perché e per quanto tempo.", PRIVACY_HTML),
        "/termini/": ("Termini e condizioni", "Termini e condizioni del servizio di invio della disdetta via PEC di Disdetta Abbonamento.", TERMINI_HTML),
    }
    for p, (t, d, b) in statiche.items():
        write(p, page(f"{t} | {SITE}", d, p, b)); urls.append(p)
    write("/completa-ordine/", page(f"Completa il tuo ordine | {SITE}", "Completa l'ordine di invio della disdetta via PEC.", "/completa-ordine/",
          COMPLETA_HTML + f'<script>window.DEPOSITO_URL={json.dumps(DEPOSITO_URL)};</script>', noindex=True,
          extra_head='<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js" defer></script>'))
    open(os.path.join(OUT, "style.css"), "w").write(CSS)
    open(os.path.join(OUT, "app.js"), "w").write(JS)
    json.dump([{"n": b["nome"], "u": f"/disdetta-{b['slug']}/", "c": CATEGORIE[b["categoria"]]["nome"], "cc": b["categoria"], "i": iniziali(b["nome"]), "l": etichetta(b)} for b in brands],
              open(os.path.join(OUT, "operatori.json"), "w", encoding="utf-8"), ensure_ascii=False)
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {ua}\nAllow: /\n\n" for ua in ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "PerplexityBot", "ClaudeBot", "Claude-SearchBot", "Google-Extended", "Applebot-Extended", "Bingbot"]) + f"Sitemap: {DOMAIN}/sitemap.xml\n")
    llms = [f"# {SITE}", "", f"> Indirizzi PEC e postali verificati, preavviso, costi e lettera di disdetta gratuita per {len(brands)} operatori italiani (telefonia, pay TV, luce e gas, assicurazioni, banche, palestre). Ogni scheda riporta la data di verifica e le fonti ufficiali. Servizio opzionale di invio via PEC a 7,90 EUR.", "", f"Ultimo aggiornamento: {TODAY}", "", "## Schede operatore"]
    for b in sorted(brands, key=lambda x: x["nome"].lower()):
        r = []
        if b.get("pec"): r.append("PEC " + b["pec"])
        if b.get("preavviso"): r.append("preavviso " + (b["preavviso"] if len(b["preavviso"]) <= 90 else b["preavviso"][:90].rsplit(" ", 1)[0] + "…"))
        llms.append(f"- [Disdetta {b['nome']}]({DOMAIN}/disdetta-{b['slug']}/): " + ("; ".join(r) if r else "disdetta online dai canali ufficiali") + f" (verificato {b['data_verifica']})")
    llms += ["", "## Pagine", f"- [Come funziona]({DOMAIN}/come-funziona/)", f"- [Termini del servizio PEC]({DOMAIN}/termini/)", f"- [Chi siamo]({DOMAIN}/chi-siamo/)"]
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write("\n".join(llms) + "\n")
    sm = "".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    for src, dst in [("brand/icon-512.png", "favicon.png"), ("brand/icon-512.png", "apple-touch-icon.png"), ("brand/og.png", "og.png"), ("brand/BingSiteAuth.xml", "BingSiteAuth.xml"), ("brand/louis.jpg", "louis.jpg")]:
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
