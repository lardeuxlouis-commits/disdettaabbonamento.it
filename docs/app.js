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
  document.getElementById('azioni').style.display='block'; el.scrollIntoView({behavior:'smooth',block:'start'});
  return false;
}
function calcScad(f,gg){try{var v=f.d.value;if(!v)return false;var sc=new Date(v+'T12:00:00');var lim=new Date(sc);lim.setDate(lim.getDate()-gg);var oggi=new Date();oggi.setHours(12,0,0,0);var diff=Math.round((lim-oggi)/86400000);var fmt=function(d){return d.toLocaleDateString('it-IT',{day:'numeric',month:'long',year:'numeric'})};var o=f.querySelector('.dlout');
 if(diff<0){o.innerHTML='<b>Sei oltre il termine</b>: con '+gg+' giorni di preavviso andava inviata entro il '+fmt(lim)+'. Invia comunque oggi: il recesso varrà per la scadenza successiva, e prima invii meno paghi.';}
 else if(diff===0){o.innerHTML='<b>Ultimo giorno utile: oggi.</b> Invia la disdetta entro stasera, meglio via PEC che fa fede della data.';}
 else{o.innerHTML='<b>Invia entro il '+fmt(lim)+'</b>, cioè tra '+diff+' giorn'+(diff===1?'o':'i')+'. Dopo quella data l\'operatore può considerare il contratto rinnovato.';}
 o.style.display='block';if(window.goatcounter)goatcounter.count({path:'calcolo-scadenza'+location.pathname,title:'Calcolo scadenza',event:true});}catch(e){}return false;}
(function(){document.addEventListener('click',function(e){var a=e.target.closest('a[data-pec]');if(a&&window.goatcounter){goatcounter.count({path:'clic-pec'+location.pathname,title:'Clic Invia via PEC',event:true});}});var fl=document.getElementById('form-lettera');if(fl){fl.addEventListener('submit',function(){if(window.goatcounter)goatcounter.count({path:'lettera-generata'+location.pathname,title:'Lettera generata',event:true});});}})();
(function(){document.querySelectorAll('[data-cd]').forEach(function(el){var end=new Date(el.dataset.cd+'T23:59:59');var d=Math.ceil((end-new Date())/86400000);if(d>0&&d<=45)el.textContent='Mancano '+d+' giorn'+(d===1?'o':'i')+'.';});})();
(function(){var el=document.querySelector('[data-proof]');if(!el||!window.fetch)return;var slug=el.dataset.proof;var base='https://disdetta.goatcounter.com/counter/';function g(p){return fetch(base+p+'.json').then(function(r){return r.ok?r.json():null}).catch(function(){return null})}
 Promise.all([g('/disdetta-'+slug+'/'),g('/lettera-generata/disdetta-'+slug+'/')]).then(function(r){var v=r[0]&&+r[0].count||0,l=r[1]&&+r[1].count||0;var parts=[];if(v>=50)parts.push('👀 Scheda consultata <b>'+v.toLocaleString('it-IT')+'</b> volte');if(l>=10)parts.push('✉️ <b>'+l.toLocaleString('it-IT')+'</b> lettere generate da questa pagina');if(parts.length){el.innerHTML=parts.join(' · ');el.hidden=false;}});})();
function chiudiSlide(){var s=document.getElementById('slidein');if(s){s.hidden=true;try{sessionStorage.setItem('slide','1')}catch(e){}}}
(function(){var s=document.getElementById('slidein');if(!s)return;try{if(sessionStorage.getItem('slide'))return;}catch(e){}var shown=false;function onS(){if(shown)return;var h=document.documentElement;var r=(h.scrollTop)/(h.scrollHeight-h.clientHeight);if(r>.55){shown=true;s.hidden=false;requestAnimationFrame(function(){s.classList.add('in')});if(window.goatcounter)goatcounter.count({path:'slidein-mostrato'+location.pathname,title:'Slide-in mostrato',event:true});window.removeEventListener('scroll',onS);}}window.addEventListener('scroll',onS,{passive:true});})();
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
