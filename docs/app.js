
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
function copiaPec(b,v){navigator.clipboard.writeText(v).then(()=>{b.textContent='Copiato';setTimeout(()=>b.textContent='Copia',1500)})}
function filtra(q){q=q.toLowerCase().trim();document.querySelectorAll('[data-nome]').forEach(c=>{c.style.display=!q||c.dataset.nome.includes(q)?'':'none'})}
