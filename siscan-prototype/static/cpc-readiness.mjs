// Consulta de entradas: não executa combate nem publica efeitos.
export function createReadinessController({request,render,onForbidden=()=>{},confirmDiscard=()=>true}){
 const blank=()=>({preparation:null,hypotheses:null,result:null,busy:false,dirty:false,error:''});let s=blank(),generation=0;
 const emit=()=>render(structuredClone(s));
 const invalidate=()=>{++generation;s.result=null;s.busy=false;s.error='';emit();};
 const api={
  setPreparation(p){++generation;s=blank();s.preparation=p?structuredClone(p):null;emit();},
  edit(value){s.hypotheses=structuredClone(value);s.dirty=true;invalidate();},invalidate,
  canLeave(){if(s.dirty&&!confirmDiscard('As hipóteses são transitórias. Descartar a edição e sair?'))return false;const p=s.preparation;api.setPreparation(p);return true;},
  async check(){
   if(!s.preparation||s.busy)return false;const p=s.preparation,token=++generation;s.busy=true;s.error='';s.result=null;emit();
   const body={selection:Object.fromEntries(p.parties.map(t=>[t.team,{group_id:t.group_id,expected_revision:t.composition_revision}])),expected_view_sha256:p.view_sha256};
   if(s.hypotheses!==null)body.hypotheses=structuredClone(s.hypotheses);
   try{
    const value=await request('/api/cpc/trial-readiness',{body});if(token!==generation)return false;
    if(value.schema_version!=='siscan-cpc-trial-readiness-01'||value.exercise_id!==p.exercise_id||value.scenario_version!==p.scenario_version||value.view_sha256!==p.view_sha256||value.official_calculation_ready!==false||value.simulation_started!==false||value.official_effects_applied!==false||typeof value.ready_for_controlled_trial!=='boolean'||!['units','excluded','issues','warnings'].every(k=>Array.isArray(value[k]))||value.ready_for_controlled_trial&&value.issues.length)throw Error('A resposta não corresponde ao par e ao contrato de prontidão.');
    s.result=value;s.busy=false;emit();return true;
   }catch(e){if(token===generation){if([401,403].includes(e.status)){s=blank();onForbidden();}s.error=e.message;s.busy=false;emit();}return false;}
  }
 };return api;
}
export function installReadinessPanel({container,csrf,onBack,onForbidden}){
 const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
 const heading=el('h3','Prontidão das entradas'),notice=el('p'),error=el('p'),summary=el('div'),check=el('button','Conferir entradas'),back=el('button','Voltar ao julgamento');
 notice.setAttribute('role','status');error.setAttribute('role','alert');error.className='siscan-group-error';check.type=back.type='button';
 container.append(heading,el('small','Conferência didática. Não executa combate nem aplica resultado.'),notice,error,summary,check,back);
 const controller=createReadinessController({request:async(path,options)=>{
  const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),15000);
  try{const response=await fetch(path,{method:'POST',signal:abort.signal,headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(options.body)});const data=await response.json();if(!response.ok)throw Object.assign(Error(data.error||'Prontidão indisponível.'),{status:response.status});return data;}finally{clearTimeout(timer);}
 },onForbidden,confirmDiscard:message=>window.confirm(message),render:s=>{
  check.disabled=s.busy||!s.preparation;notice.textContent=s.busy?'Conferindo fontes…':s.result?({incomplete:'Entradas incompletas',unsupported:'Recorte não suportado',ready:'Entradas prontas para ensaio controlado'})[s.result.status]:'Confira as entradas do par preparado.';error.textContent=s.error;summary.replaceChildren();
  if(s.result){for(const unit of s.result.units){const items=s.result.issues.filter(i=>i.unit_id===unit.unit_id),section=el('details');section.append(el('summary',unit.team+' · '+unit.code+' · '+items.length+' pendências'));for(const i of items)section.append(el('p',i.message),el('small',i.action));summary.append(section);}for(const i of s.result.issues.filter(i=>!i.unit_id))summary.append(el('p',i.message));for(const u of s.result.excluded)summary.append(el('p',u.code+' · '+u.reason));}
 }});
 check.onclick=()=>controller.check();back.onclick=()=>{if(controller.canLeave())onBack();};return controller;
}
