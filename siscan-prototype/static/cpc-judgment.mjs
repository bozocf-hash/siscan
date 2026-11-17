import {judgmentStage} from './map-presentation.mjs';
// Julgamento didático; estado oficial só muda pelo comando explícito do instrutor.
export function createJudgmentController({request,render,onOfficial,confirmDiscard=()=>true,onForbidden=()=>{},onResumePair=()=>{}}){
 const blank=()=>({preparation:null,basis:null,drafts:{},reason:'',preview:null,proposal:null,view:null,receipt:null,
  history:[],nextCursor:null,correction:null,busy:false,dirty:false,confirming:false,pending:null,error:'',notice:'',refreshPending:false});
 let s=blank(),generation=0;
 const emit=()=>render(structuredClone(s));
 const selection=p=>Object.fromEntries(p.parties.map(t=>[t.team,{group_id:t.group_id,expected_revision:t.composition_revision}]));
 const editing=()=>!s.busy&&!s.pending&&!s.receipt;
 function changed(){s.dirty=true;s.preview=null;s.confirming=false;s.error='';emit();}
 function effects(){
  const result=[];
  for(const [unit_id,d] of Object.entries(s.drafts)){
   if(!d.enabled)continue;const changes={};
   if(d.indexAction==='clear')changes.index_percent=null;
   if(d.indexAction==='set'){
    const raw=String(d.indexValue).trim(),value=Number(raw);
    if(!raw||!Number.isFinite(value)||value<0||value>100)throw Error('Informe índice de 0 a 100 para cada alteração selecionada.');
    changes.index_percent=value;
   }
   if(d.lossAction==='lost')changes.lost=true;
   if(d.lossAction==='available')changes.lost=false;
   if(!Object.keys(changes).length)throw Error('Escolha a alteração de cada meio marcado.');
   result.push({unit_id,changes});
  }
  if(!result.length)throw Error('Selecione pelo menos um meio e uma alteração.');
  return result;
 }
 function content(){
  if(!s.basis)throw Error('Abra a base do julgamento.');
  if(!s.reason.trim())throw Error('Informe a justificativa.');
  const body={selection:s.basis.selection,basis_sha256:s.basis.basis_sha256,reason:s.reason,effects:effects()};
  if(s.correction)body.correction_decision_id=s.correction;return body;
 }
 async function read(job){
  if(s.busy)return false;const token=++generation;s.busy=true;s.error='';emit();
  try{const apply=await job();if(token!==generation)return false;apply();s.busy=false;s.error='';emit();return true;}
  catch(error){if(token===generation){if([401,403].includes(error.status)){s=blank();onForbidden();}s.busy=false;s.error=error.message;emit();}return false;}
 }
 async function refreshOfficial(){
  const source=s.basis?.selection,token=generation;if(!source)return;
  try{
   const fresh=await request('/api/cpc/judgments/context',{body:{selection:source}});
   if(token!==generation)return;s.basis=fresh;s.refreshPending=false;onOfficial(fresh.states);
  }catch{if(token===generation){s.refreshPending=true;s.notice='Aplicação confirmada. Atualização da vista pendente; consulte o recibo ou atualize a vista.';}}
 }
 async function write(pending){
  if(s.busy)return false;const token=++generation;s.pending=structuredClone(pending);s.busy=true;s.error='';emit();
  try{
   const result=await request(pending.path,{body:pending.body});if(token!==generation)return false;
   s.pending=null;s.dirty=false;s.confirming=false;s.error='';
   if(pending.kind==='decide'){
    s.receipt=result;s.history=s.history.map(item=>item.proposal_id===s.proposal.proposal_id?{...item,status:result.action}:item);s.notice=result.action==='confirm'?'Efeitos confirmados pelo instrutor.':'Proposta rejeitada; meios preservados.';
    if(result.action==='confirm')await refreshOfficial();
   }else{s.proposal=result;s.notice='Proposta registrada. Os efeitos ainda não foram aplicados.';}
   if(token===generation){s.busy=false;emit();}return true;
  }catch(error){if(token===generation){s.busy=false;s.error=error.message;
    if([401,403].includes(error.status)){s=blank();onForbidden();s.error=error.message;}
    if(error.status&&error.status<500)s.pending=null;
    else s.notice='Resposta não confirmada. Reenvie a mesma intenção para recuperar o recibo, sem duplicar efeitos.';
    emit();}return false;}
 }
 const api={
  setPreparation(preparation){++generation;s=blank();s.preparation=preparation;emit();},
  canLeave(){if(s.busy){s.error='Aguarde a operação em andamento.';emit();return false;}if(!s.dirty&&!s.pending)return true;
   const accepted=confirmDiscard('Há edição não salva ou resposta pendente. Sair preserva propostas registradas. Deseja sair?');
   if(accepted){const {preparation,history,nextCursor}=s;s={...blank(),preparation,history,nextCursor};emit();}return accepted;},
  async open(){if(!s.preparation||!api.canLeave())return false;const p=s.preparation;
   return read(async()=>{const base=await request('/api/cpc/judgments/context',{body:{selection:selection(p),expected_view_sha256:p.view_sha256}});
    return()=>{s={...blank(),preparation:p,basis:base,busy:true,notice:'Base oficial conferida. Selecione os meios, informe as alterações e confira a prévia.'};onOfficial(base.states);};});},
  edit(uid,patch){if(!editing()||!s.basis?.states[uid])return;s.drafts[uid]={enabled:false,indexAction:'keep',indexValue:'',lossAction:'keep',...s.drafts[uid],...patch};changed();},
  reason(value){if(!editing())return;s.reason=value;changed();},
  async preview(){if(!editing())return false;let body;try{body=content();}catch(e){s.error=e.message;emit();return false;}
   return read(async()=>{const value=await request('/api/cpc/judgments/preview',{body});return()=>{s.preview=value;s.notice='Prévia didática. Nenhum efeito aplicado.';};});},
  async save(){if(!editing()||!s.preview)return false;const body={...content(),command_id:crypto.randomUUID()};let path='/api/cpc/judgments';
   if(s.proposal){path+='/'+s.proposal.proposal_id+'/revisions';body.expected_revision=s.proposal.revision;body.expected_sha256=s.proposal.body_sha256;delete body.correction_decision_id;}
   return write({path,body,kind:'save'});},
  review(){if(!s.proposal||s.dirty||!s.preview||s.busy||s.pending||s.receipt)return false;s.confirming=true;emit();return true;},
  cancelReview(){s.confirming=false;emit();},
  async decide(action){
   if(!s.proposal||s.dirty||s.busy||s.pending||s.receipt||(action==='confirm'&&!s.confirming))return false;
   return write({kind:'decide',path:'/api/cpc/judgments/'+s.proposal.proposal_id+'/decisions',body:{
    command_id:crypto.randomUUID(),expected_revision:s.proposal.revision,expected_sha256:s.proposal.body_sha256,action,reason:s.reason}});
  },
  retry(){return s.pending?write(s.pending):Promise.resolve(false);},
  async refresh(){if(s.busy)return;await refreshOfficial();emit();},
  async history(cursor=0){if(!api.canLeave())return false;
   return read(async()=>{const list=await request('/api/cpc/judgments?limit=20&cursor='+cursor);return()=>{s.history=cursor?[...s.history,...list.items]:list.items;s.nextCursor=list.next_cursor;s.notice=s.history.length?'Selecione um julgamento do histórico. Propostas pendentes não são efeitos oficiais.':'Nenhum julgamento registrado neste exercício.';};});},
  async resume(id){if(!api.canLeave())return false;return read(async()=>{
   const view=await request('/api/cpc/judgments/'+encodeURIComponent(id));const base=view.current.body.origin.basis;
   let value=null;
   if(!view.decision&&view.available){const b={selection:base.selection,basis_sha256:base.basis_sha256,reason:view.current.body.reason,
     effects:view.current.body.effects.map(e=>({unit_id:e.refs.unit_id,changes:e.changes}))};if(view.correction_decision_id)b.correction_decision_id=view.correction_decision_id;
    value=await request('/api/cpc/judgments/preview',{body:b});}
   return()=>{const p=value?value.basis.preparation:s.preparation,h=s.history;s={...blank(),preparation:p,basis:base,history:h,view,busy:true,
    reason:view.current.body.reason,correction:view.correction_decision_id,proposal:{proposal_id:id,revision:view.current.revision,body_sha256:view.current.body_sha256},
    preview:value,receipt:view.receipt,notice:view.decision?'Decisão do histórico; consultar o planejamento para estado atual.':view.availability_reason||'Proposta retomada; efeitos ainda não aplicados.'};
    for(const e of view.current.body.effects){const c=e.changes;s.drafts[e.refs.unit_id]={enabled:true,indexAction:'index_percent'in c?(c.index_percent===null?'clear':'set'):'keep',indexValue:c.index_percent??'',lossAction:'lost'in c?(c.lost?'lost':'available'):'keep'};}
    if(value){if(onResumePair(value.basis.preparation)===false){s.preview=null;s.notice='Atualize os grupos CPC e retome a proposta para conferir o par no mapa.';}else onOfficial(value.basis.states);}
   };});},
  async correct(){if(s.receipt?.action!=='confirm'||s.busy)return false;const correction=s.receipt.decision_id,p=s.preparation,source=p?selection(p):s.basis.selection;
   return read(async()=>{const base=await request('/api/cpc/judgments/context',{body:{selection:source}});return()=>{
    s={...blank(),preparation:p,basis:base,correction,busy:true,notice:'Nova proposta de correção; decisão anterior preservada.'};onOfficial(base.states);};});}
 };
 return api;
}

export function installJudgmentPanel({container,csrf,onOfficial,onForbidden,onResumePair}){
 const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
 container.classList.add('siscan-judgment');
 const style=el('style');style.textContent='.siscan-judgment{border-top:1px solid #7995aa;margin-top:14px;padding-top:12px}.siscan-judgment label{display:block;margin:10px 0}.siscan-judgment input:not([type=checkbox]),.siscan-judgment select,.siscan-judgment textarea{display:block;width:100%;box-sizing:border-box;padding:8px;background:#18354d;color:#fff;border:1px solid #7995aa;border-radius:4px}.siscan-judgment fieldset{margin:12px 0;padding:10px;border:1px solid #7995aa;border-radius:6px}.siscan-judgment small{display:block;overflow-wrap:anywhere}.siscan-judgment button{margin:5px 5px 5px 0}.siscan-judgment .judgment-final{border:2px solid #ffd27a;padding:10px}.siscan-judgment .judgment-error{color:#ffb7b7}.siscan-judgment [hidden]{display:none!important}';container.append(style);
 const heading=el('h3','2 · Definir efeitos'),notice=el('p'),error=el('p'),form=el('div'),reason=el('textarea'),
  previewBox=el('section'),final=el('section'),receipt=el('p'),historyBox=el('section');
 heading.tabIndex=-1;notice.setAttribute('role','status');notice.setAttribute('aria-live','polite');notice.tabIndex=-1;error.setAttribute('role','alert');error.className='judgment-error';
 reason.rows=2;reason.maxLength=4000;reason.setAttribute('aria-label','Justificativa do julgamento');
 const reasonLabel=el('label','Justificativa do instrutor');reasonLabel.append(reason);
 const controls={};const button=(key,text,host=container)=>{const b=el('button',text);b.type='button';controls[key]=b;host.append(b);return b;};
 const steps=el('ol');steps.className='siscan-judgment-steps';steps.setAttribute('aria-label','Etapas do julgamento');for(const label of ['Efeitos','Revisão','Confirmação','Resultado'])steps.append(el('li',label));container.append(steps,heading,notice,error);
 button('open','Definir efeitos');button('history','Retomar julgamento');container.append(form,reasonLabel);
 button('preview','Revisar efeitos');container.append(previewBox);button('edit','Editar efeitos');button('save','Salvar proposta');
 button('review','Avançar para confirmação');button('reject','Rejeitar proposta');
 final.className='judgment-final';final.append(el('strong','Revisão final — aplicação oficial'),el('p','Confirme somente a revisão e os efeitos exibidos na prévia.'));
 button('apply','Confirmar aplicação',final);button('cancel','Cancelar aplicação',final);container.append(final,receipt);
 button('retry','Reenviar mesma intenção');button('refresh','Atualizar vista oficial');button('correct','Nova proposta de correção');
 container.append(historyBox);button('more','Mais julgamentos');
 let controller,controllerState,lastBasis=null,lastStage=null,inputs=new Map(),wasBusy=false,lastFocused=null;
 let editingPreview=false;
 const textState=value=>`${value.index_percent===null?'não avaliado':value.index_percent+'%'} · ${value.lost===null?'perda não avaliada':value.lost?'perda confirmada':'não perdido'}`;
 function memberName(basis,uid){for(const p of basis?.preparation.parties||[]){const m=p.members.find(x=>x.unit_id===uid);if(m)return p.team+' · '+m.code+' · '+m.name;}return uid;}
 function makeSelect(label,options){const l=el('label',label.split(' · ')[0]),select=el('select');select.setAttribute('aria-label',label);for(const [value,text] of options){const o=el('option',text);o.value=value;select.append(o);}l.append(select);return [l,select];}
 function render(s){
  controllerState=s;
  if(s.busy&&!wasBusy)lastFocused=document.activeElement;const completed=wasBusy&&!s.busy;wasBusy=s.busy;
  const stage=editingPreview&&s.basis&&!s.receipt&&!s.confirming?'edit':judgmentStage(s);
  container.dataset.stage=stage;heading.textContent=({start:'2 · Definir efeitos',edit:'2 · Definir efeitos',preview:'3 · Revisar efeitos',saved:'3 · Proposta salva',unavailable:'Proposta requer conferência',confirm:'4 · Confirmar aplicação',result:'Resultado registrado'})[stage];
  const stepIndex=({start:0,edit:0,preview:1,saved:1,unavailable:1,confirm:2,result:3})[stage];[...steps.children].forEach((node,i)=>{if(i===stepIndex)node.setAttribute('aria-current','step');else node.removeAttribute('aria-current');});
  notice.textContent=s.busy?'Conferindo julgamento…':s.notice||(s.preparation?'Defina os efeitos ou retome um julgamento salvo.':'Selecione as forças ou retome um julgamento salvo.');error.textContent=s.error;
  const locked=s.busy||Boolean(s.pending)||Boolean(s.receipt),key=s.basis?.basis_sha256||null;
  if(key!==lastBasis){editingPreview=false;lastBasis=key;inputs.clear();form.replaceChildren();
   const ordered=(s.basis?.preparation.parties||[]).flatMap(p=>p.members.map(m=>m.unit_id));
   for(const uid of ordered){
    const field=el('fieldset'),legend=el('legend',memberName(s.basis,uid)),official=el('small'),check=el('input');check.type='checkbox';
    const mark=el('label',' Alterar este meio');mark.prepend(check);check.setAttribute('aria-label','Alterar '+memberName(s.basis,uid));
    const [indexLabel,index]=makeSelect('Avaliação · '+memberName(s.basis,uid),[['keep','Preservar avaliação'],['set','Definir índice (%)'],['clear','Retirar avaliação']]);
    const number=el('input');number.type='number';number.min='0';number.max='100';number.step='any';number.setAttribute('aria-label','Índice (%) · '+memberName(s.basis,uid));indexLabel.append(number);
    const [lossLabel,loss]=makeSelect('Perda · '+memberName(s.basis,uid),[['keep','Preservar declaração de perda'],['lost','Declarar perda'],['available','Declarar não perdido']]);
    const change=()=>controller.edit(uid,{enabled:check.checked,indexAction:index.value,indexValue:number.value,lossAction:loss.value});
    check.onchange=change;index.onchange=change;number.oninput=change;loss.onchange=change;
    field.append(legend,official,mark,indexLabel,lossLabel);form.append(field);inputs.set(uid,{check,index,number,loss,official});
   }
  }
  for(const [uid,n] of inputs){const d=s.drafts[uid]||{enabled:false,indexAction:'keep',indexValue:'',lossAction:'keep'};
   n.check.checked=d.enabled;n.index.value=d.indexAction;n.loss.value=d.lossAction;
   if(n.number.value!==String(d.indexValue))n.number.value=String(d.indexValue);
   n.check.disabled=locked;n.index.disabled=locked||!d.enabled;n.loss.disabled=locked||!d.enabled;n.number.disabled=locked||!d.enabled||d.indexAction!=='set';n.number.hidden=d.indexAction!=='set';n.index.closest('label').hidden=!d.enabled;n.loss.closest('label').hidden=!d.enabled;
   n.official.textContent=(s.view?'Referência registrada: ':'Estado oficial conferido: ')+textState(s.basis.states[uid].state)+' · revisão '+s.basis.states[uid].state.revision;
  }
  form.hidden=stage!=='edit';reasonLabel.hidden=stage!=='edit';reason.disabled=locked||!s.basis;if(reason.value!==s.reason)reason.value=s.reason;
  controls.open.disabled=s.busy||!s.preparation;controls.history.disabled=s.busy;
  controls.preview.disabled=locked||!s.basis;controls.save.disabled=locked||!s.preview||!s.dirty;controls.save.textContent=s.proposal?'Salvar revisão':'Salvar proposta';
  controls.review.disabled=locked||!s.proposal||s.dirty||!s.preview;controls.reject.disabled=locked||!s.proposal||s.dirty;
  for(const [key,visible] of Object.entries({open:stage==='start'||stage==='result',history:stage==='start'||stage==='result',preview:stage==='edit',save:stage==='preview',edit:['preview','saved','unavailable'].includes(stage),review:stage==='saved',reject:['saved','unavailable'].includes(stage)}))controls[key].hidden=!visible;
  const primary=({start:'open',edit:'preview',preview:'save',saved:'review',confirm:'apply',result:'open'})[stage];for(const [key,b] of Object.entries(controls))b.classList.toggle('is-primary',key===primary);
  controls.edit.disabled=locked;controls.open.textContent=stage==='result'?'Novo julgamento':'Definir efeitos';
  final.hidden=!s.confirming;controls.apply.disabled=s.busy||Boolean(s.pending);controls.cancel.disabled=s.busy;
  controls.retry.hidden=!s.pending;controls.retry.disabled=s.busy;controls.refresh.hidden=!s.refreshPending;controls.refresh.disabled=s.busy;
  controls.correct.hidden=s.receipt?.action!=='confirm';controls.correct.disabled=s.busy;
  receipt.textContent=s.receipt?`Decisão ${s.receipt.decision_id} · ${s.receipt.action==='confirm'?'efeitos confirmados':'rejeitada, sem efeitos'}`:s.proposal?`Proposta ${s.proposal.proposal_id} · revisão ${s.proposal.revision} · efeitos ainda não aplicados`:'';
  receipt.style.overflowWrap='anywhere';receipt.className='siscan-judgment-receipt';previewBox.hidden=stage==='edit';previewBox.replaceChildren();
  if(s.preview){previewBox.append(el('h4',s.receipt?s.receipt.action==='confirm'?'Efeitos confirmados nesta decisão':'Proposta rejeitada — efeitos não aplicados':'Prévia — efeitos propostos'));
   previewBox.append(el('p','Justificativa: '+s.reason));
   for(const e of s.preview.effects)previewBox.append(el('p',`${memberName(s.basis,e.unit_id)}: ${textState(e.before)} → ${textState(e.after)}`));
  }else if(s.view?.receipt?.effects){previewBox.append(el('h4','Efeitos desta decisão no histórico'));
   for(const e of s.view.receipt.effects)previewBox.append(el('p',`${memberName(s.basis,e.unit_id)}: ${textState(e.before)} → ${textState(e.after)}`));}
  historyBox.replaceChildren();if(s.history.length)historyBox.append(el('h4','Julgamentos registrados'));
  for(const item of s.history){const b=el('button',`${item.status==='pending'?'Pendente':item.status==='confirm'?'Confirmado':'Rejeitado'} · ${item.reason} · revisão ${item.revision}`);b.type='button';b.title=b.textContent;b.onclick=()=>{editingPreview=false;controller.resume(item.proposal_id);};historyBox.append(b);}
  controls.more.hidden=s.nextCursor===null;controls.more.disabled=s.busy;controls.more.onclick=()=>controller.history(s.nextCursor);
  const stageChanged=lastStage!==null&&lastStage!==stage;lastStage=stage;
  if((completed||stageChanged)&&(document.activeElement===document.body||!document.activeElement.getClientRects().length)){if(lastFocused?.isConnected&&!lastFocused.disabled&&lastFocused.getClientRects().length)lastFocused.focus({preventScroll:true});else heading.focus({preventScroll:true});}
 }
 const request=async(path,options)=>{
  const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),15000);
  try{const response=await fetch(path,{signal:abort.signal,...(options?{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(options.body)}:{})});
   const data=await response.json();if(!response.ok)throw Object.assign(Error(data.error||'Julgamento indisponível.'),{status:response.status});return data;
  }finally{clearTimeout(timer);}
 };
 controller=createJudgmentController({request,render,onOfficial,onForbidden,onResumePair,confirmDiscard:message=>window.confirm(message)});
 reason.oninput=()=>controller.reason(reason.value);controls.edit.onclick=()=>{editingPreview=true;render(controllerState);};
 for(const [key,action] of Object.entries({open:()=>{editingPreview=false;return controller.open();},history:()=>controller.history(),preview:()=>{editingPreview=false;return controller.preview();},save:()=>controller.save(),
  review:()=>controller.review(),apply:()=>controller.decide('confirm'),cancel:()=>controller.cancelReview(),reject:()=>controller.decide('reject'),
  retry:()=>controller.retry(),refresh:()=>controller.refresh(),correct:()=>{editingPreview=false;return controller.correct();}}))controls[key].onclick=action;
 return controller;
}
