# Génère l'aperçu HTML + le JSON des 9 groupes de la campagne test (31/10/2026)
import json, html
BASE="https://disdettaabbonamento.it"
UTM="?utm_source=google&utm_medium=cpc&utm_campaign=pec-test"
def grp(name, path, kws, marca, extra_h, d1):
    H=[f"Disdetta {marca} via PEC","Te la inviamo noi, 7,90 €","Ricevuta con valore legale","Prima della scadenza","Indirizzo PEC verificato","Lettera pronta in 1 minuto","Senza PEC, senza posta","Vale come raccomandata A/R"]+extra_h
    D=[d1,"Niente PEC, niente posta: inviamo noi la disdetta e ti giriamo le ricevute via e-mail.","Lettera gratis da compilare, o invio PEC a 7,90 € con ricevuta entro 2 giorni lavorativi."]
    return dict(name=name,url=BASE+path+UTM,path1=path.strip("/").replace("disdetta-","").split("-")[0][:15],path2="pec",keywords=kws,headlines=H,descriptions=D)
G=[
 grp("Generali","/disdetta-generali-italia/",["disdetta generali pec","pec generali per disdetta","disdetta polizza generali","disdetta generali come fare","generali disdetta polizza pec"],"Generali",["Disdetta polizza Generali","Preavviso verificato"],"PEC e preavviso di Generali verificati su fonti ufficiali. Lettera pronta, inviamo noi."),
 grp("Allianz","/disdetta-allianz-italia/",["disdetta allianz pec","pec allianz per disdetta","disdetta polizza allianz","disdetta allianz direct","allianz disdetta polizza come fare"],"Allianz",["Disdetta polizza Allianz","Preavviso verificato"],"PEC e preavviso di Allianz verificati su fonti ufficiali. Lettera pronta, inviamo noi."),
 grp("Unipol","/disdetta-unipol/",["disdetta unipol pec","pec unipolsai disdetta","disdetta polizza unipolsai","unipol disdetta polizza come fare"],"Unipol",["Disdetta polizza UnipolSai","Preavviso verificato"],"PEC e preavviso di UnipolSai verificati su fonti ufficiali. Lettera pronta, inviamo noi."),
 grp("AXA","/disdetta-axa-italia/",["disdetta axa pec","pec axa assicurazioni disdetta","disdetta polizza axa","axa disdetta polizza come fare"],"AXA",["Disdetta polizza AXA","Preavviso verificato"],"PEC e preavviso di AXA verificati su fonti ufficiali. Lettera pronta, inviamo noi."),
 grp("Cattolica","/disdetta-cattolica-assicurazioni/",["disdetta cattolica pec","disdetta polizza cattolica","cattolica assicurazioni disdetta pec"],"Cattolica",["Disdetta polizza Cattolica","Preavviso verificato"],"PEC e preavviso di Cattolica verificati su fonti ufficiali. Lettera pronta, inviamo noi."),
 grp("Prima","/disdetta-prima-assicurazioni/",["disdetta prima assicurazioni pec","pec prima assicurazioni","disdetta polizza prima","prima.it disdetta"],"Prima",["Disdetta polizza Prima","Preavviso verificato"],"PEC e preavviso di Prima Assicurazioni verificati. Lettera pronta, la inviamo noi."),
 grp("Verisure","/disdetta-verisure-italia/",["disdetta verisure pec","recesso verisure","come disdire verisure","disdetta contratto verisure"],"Verisure",["Recesso Verisure via PEC","Preavviso verificato"],"PEC e preavviso di Verisure verificati su fonti ufficiali. Lettera pronta, inviamo noi."),
 grp("Polizza generica","/",["disdetta polizza via pec","disdetta assicurazione pec","inviare disdetta polizza","lettera disdetta polizza","disdetta polizza auto come fare"],"polizza",["Disdetta assicurazione PEC","Preavviso verificato"],"PEC e preavviso della tua assicurazione verificati. Lettera pronta, la inviamo noi."),
 grp("Sky (testimone)","/disdetta-sky/",["disdetta sky pec","inviare disdetta sky","modulo disdetta sky","disdetta sky raccomandata"],"Sky",["Modulo disdetta Sky pronto","Preavviso verificato"],"PEC e preavviso di Sky verificati su fonti ufficiali. Lettera pronta, inviamo noi."),
]
G[7]["path1"]="polizza"; G[8]["path1"]="sky"
err=[]
for g in G:
    for h in g["headlines"]:
        if len(h)>30: err.append((g["name"],"titre",len(h),h))
    for d in g["descriptions"]:
        if len(d)>90: err.append((g["name"],"desc",len(d),d))
print("erreurs:",err)
json.dump(G,open("gruppi.json","w"),ensure_ascii=False,indent=1)
css="body{font-family:-apple-system,Arial,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#202124}h1{font-size:22px}h2{font-size:17px;margin:34px 0 6px;border-bottom:2px solid #1a73e8;padding-bottom:4px}.ad{border:1px solid #dadce0;border-radius:12px;padding:14px 16px;margin:10px 0;background:#fff}.sp{font-size:11px;font-weight:700;color:#202124}.url{font-size:13px;color:#202124;margin:2px 0 4px}.t{color:#1a0dab;font-size:19px;line-height:1.25;margin:0 0 4px}.d{font-size:14px;color:#4d5156;line-height:1.5}.kw{font-size:13px;color:#555;margin:6px 0}.kw code{background:#f1f3f4;padding:2px 6px;border-radius:4px;margin:2px;display:inline-block}.all{font-size:12px;color:#5f6368;margin-top:8px}.all span{display:inline-block;background:#e8f0fe;color:#174ea6;border-radius:4px;padding:2px 6px;margin:2px}p.i{font-size:14px;color:#444}"
out=[f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Annonces Google à valider</title><style>{css}</style></head><body><h1>Les 9 annonces avant publication</h1><p class='i'>Pour chaque groupe : un exemple de rendu tel que Google l'affiche (3 titres et 2 descriptions tirés de la liste, Google compose lui même), puis la liste complète des titres, des descriptions et des mots clés qui déclenchent l'annonce. Campagne : Italie, italien, 7 € par jour, du 31/10 au 15/11, clic plafonné à 0,35 €.</p>"]
for g in G:
    H=g["headlines"];D=g["descriptions"]
    out.append(f"<h2>{html.escape(g['name'])}</h2><div class='ad'><div class='sp'>Sponsorizzato</div><div class='url'>disdettaabbonamento.it › {html.escape(g['path1'])} › pec</div><div class='t'>{html.escape(H[0])} | {html.escape(H[1])} | {html.escape(H[2])}</div><div class='d'>{html.escape(D[0])} {html.escape(D[1])}</div></div>")
    out.append("<div class='all'><b>Titres</b> "+"".join(f"<span>{html.escape(h)}</span>" for h in H)+"<br><b>Descriptions</b> "+"".join(f"<span>{html.escape(d)}</span>" for d in D)+"</div>")
    out.append("<div class='kw'><b>Mots clés (expression)</b><br>"+"".join(f"<code>\"{html.escape(k)}\"</code>" for k in g["keywords"])+f"<br><b>Page d'arrivée</b> {html.escape(g['url'].split('?')[0])}</div>")
out.append("</body></html>")
open("apercu-annonces.html","w").write("".join(out))
print("ok", len(G), "groupes")
