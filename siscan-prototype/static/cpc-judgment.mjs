// Julgamento didático; estado oficial só muda pelo comando explícito do instrutor.
export function createJudgmentController({request,render,onOfficial,confirmDiscard=()=>true,onForbidden=()=>{}}){
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
  try{const apply=await job();if(token!==generation)return false;apply();s.busy=false;emit();return true;}
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
   s.pending=null;s.dirty=false;s.confirming=false;
   if(pending.kind==='decide'){
    s.receipt=result;s.notice=result.action==='confirm'?'Efeitos confirmados pelo instrutor.':'Proposta rejeitada; meios preservados.';
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
  canLeave(){if(s.busy){s.error='Aguarde a operação em andamento.';emit();return false;}return (!s.dirty&&!s.pending)||confirmDiscard('Há edição não salva ou resposta pendente. Sair preserva propostas registradas. Deseja sair?');},
  async open(){if(!s.preparation||!api.canLeave())return false;const p=s.preparation;
   return read(async()=>{const base=await request('/api/cpc/judgments/context',{body:{selection:selection(p),expected_view_sha256:p.view_sha256}});
    return()=>{s={...blank(),preparation:p,basis:base,busy:true};onOfficial(base.states);};});},
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
   return read(async()=>{const list=await request('/api/cpc/judgments?limit=20&cursor='+cursor);return()=>{s.history=cursor?[...s.history,...list.items]:list.items;s.nextCursor=list.next_cursor;};});},
  async resume(id){if(!api.canLeave())return false;return read(async()=>{
   const view=await request('/api/cpc/judgments/'+encodeURIComponent(id));const base=view.current.body.origin.basis;
   let value=null;
   if(!view.decision&&view.available){const b={selection:base.selection,basis_sha256:base.basis_sha256,reason:view.current.body.reason,
     effects:view.current.body.effects.map(e=>({unit_id:e.refs.unit_id,changes:e.changes}))};if(view.correction_decision_id)b.correction_decision_id=view.correction_decision_id;
    value=await request('/api/cpc/judgments/preview',{body:b});}
   return()=>{const p=s.preparation,h=s.history;s={...blank(),preparation:p,basis:base,history:h,view,busy:true,
    reason:view.current.body.reason,correction:view.correction_decision_id,proposal:{proposal_id:id,revision:view.current.revision,body_sha256:view.current.body_sha256},
    preview:value,receipt:view.receipt,notice:view.decision?'Decisão do histórico; consultar o planejamento para estado atual.':view.availability_reason||'Proposta retomada; efeitos ainda não aplicados.'};
    for(const e of view.current.body.effects){const c=e.changes;s.drafts[e.refs.unit_id]={enabled:true,indexAction:'index_percent'in c?(c.index_percent===null?'clear':'set'):'keep',indexValue:c.index_percent??'',lossAction:'lost'in c?(c.lost?'lost':'available'):'keep'};}
   };});},
  async correct(){if(s.receipt?.action!=='confirm'||s.busy)return false;const correction=s.receipt.decision_id,p=s.preparation,source=s.basis.selection;
   return read(async()=>{const base=await request('/api/cpc/judgments/context',{body:{selection:source}});return()=>{
    s={...blank(),preparation:p,basis:base,correction,busy:true,notice:'Nova proposta de correção; decisão anterior preservada.'};onOfficial(base.states);};});}
 };
 return api;
}
