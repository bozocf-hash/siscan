// Consulta de composição: não envia comandos de plotagem ou execução CPC.
export function createGroupController({request,render,highlight,focus,commandId=()=>crypto.randomUUID()}) {
 let epoch=0,retry=null;
 let state={team:null,data:null,selectedGroup:null,selectedMember:null,loading:false,busy:false,error:'',notice:''};
 const emit=()=>render(structuredClone(state));
 const group=()=>state.data?.groups.find(g=>g.group_id===state.selectedGroup);
 const visibleMember=id=>state.data?.units.find(u=>u.asset_id===id)||group()?.members.find(m=>m.asset_id===id);
 const ids=()=>state.selectedMember!==null?(visibleMember(state.selectedMember)?[state.selectedMember]:[]):group()?.members.map(m=>m.asset_id).filter(Number.isInteger)||[];
 function select(id){state.selectedMember=null;state.selectedGroup=state.data?.groups.some(g=>g.group_id===id)?id:null;highlight(ids());emit();}
 async function load(team){
  const token=++epoch;if(team!==state.team)retry=null;
  state={team,data:null,selectedGroup:null,selectedMember:null,loading:true,busy:false,error:'',notice:''};highlight([]);emit();
  try{
   const result=await request('/api/map-unit-groups?team='+encodeURIComponent(team));
   if(token!==epoch)return false;
   if(result.team!==team||!Array.isArray(result.groups)||!Array.isArray(result.units)||result.storage!=='memory')throw Error('Resposta de grupamentos inválida.');
   state.data=result;state.loading=false;emit();return true;
  }catch(error){if(token===epoch){state.data=null;state.loading=false;state.error=error.message;emit();}return false;}
 }
 async function write(path,body){
  if(state.loading||state.busy||!state.data?.exercise_open)return false;
  const token=epoch,team=state.team,intent=JSON.stringify([path,body]);
  if(retry?.intent!==intent)retry={intent,payload:{...body,command_id:commandId()}};
  const payload=retry.payload;state.busy=true;state.error='';emit();
  try{
   const result=await request(path,{method:'POST',body:payload});
   if(token!==epoch)return false;
   retry=null;
   if(await load(team)){
    select(result.group.group_id);state.notice=path.endsWith('/archive')?'Grupamento arquivado.':'Grupamento criado.';emit();
   }
   return true;
  }catch(error){if(token===epoch){state.busy=false;state.error=error.message;emit();}return false;}
 }
 return {load,select,inspectMember:id=>{state.selectedMember=id;highlight(ids());emit();},
  create:({designation,domain,member_unit_ids})=>write('/api/map-unit-groups',{
   team:state.team,designation:designation.trim(),domain,member_unit_ids:[...member_unit_ids].sort()}),
  archive:id=>{const g=state.data?.groups.find(g=>g.group_id===id);return g?.active?
   write('/api/map-unit-groups/'+encodeURIComponent(id)+'/archive',{
    team:state.team,expected_revision:g.composition_revision}):Promise.resolve(false);},
  focusSelected:()=>focus(ids()),reapplyHighlight:()=>highlight(ids())};
}

export function installGroupPanel({container,csrf,highlight,focus}) {
 const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
 const title=el('h2','Grupamentos'),warning=el('p','Grupamentos temporários: se perdem ao reiniciar o servidor.'),
  status=el('p'),refresh=el('button','Atualizar grupamentos'),list=el('div'),details=el('div'),form=el('form');
 warning.className='siscan-group-warning';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 refresh.type='button';list.setAttribute('aria-label','Grupamentos do partido');
 const designation=el('input'),domain=el('select'),choices=el('fieldset'),legend=el('legend','Integrantes disponíveis'),
  submit=el('button','Criar grupamento');
 designation.required=true;designation.maxLength=120;designation.setAttribute('aria-label','Designação do grupamento');
 for(const [value,text] of [['aereo','Aéreo'],['naval','Naval']]){const o=el('option',text);o.value=value;domain.append(o);}
 domain.setAttribute('aria-label','Domínio do grupamento');choices.append(legend);submit.type='submit';
 const nameLabel=el('label','Designação'),domainLabel=el('label','Domínio');nameLabel.append(designation);domainLabel.append(domain);
 form.append(el('h3','Nova composição'),nameLabel,domainLabel,choices,submit);container.append(title,warning,status,refresh,list,details,form);
 let current=null,lastTeam=null,desiredFocus=null,archivePending=null;const selected=new Set();submit.dataset.groupFocus='create';
 function render(state){
  const active=document.activeElement;
  if(active?.dataset.groupFocus)desiredFocus=active.dataset.groupFocus;
  else if(active!==document.body)desiredFocus=null;
  current=state;if(lastTeam!==state.team){lastTeam=state.team;designation.value='';selected.clear();}
  if(state.selectedGroup!==archivePending)archivePending=null;
  status.textContent=state.error||state.notice||(state.loading?'Carregando grupamentos…':`Partido ${state.team||''} · ${state.data?.groups.length||0} grupamentos`);
  status.className=state.error?'siscan-group-error':'';refresh.disabled=state.loading||state.busy;
  warning.textContent=state.data?.warning||'Grupamentos temporários: se perdem ao reiniciar o servidor.';
  list.replaceChildren();details.replaceChildren();
  if(state.data&&!state.data.groups.length)list.append(el('p','Nenhum grupamento cadastrado neste processo.'));
  for(const g of state.data?.groups||[]){
   const button=el('button',`${g.designation} · revisão ${g.composition_revision} · ${g.active?'Ativo':'Arquivado'}${g.needs_review?' · Conferência pendente':''}`);
   button.dataset.groupFocus='group:'+g.group_id;
   button.type='button';button.setAttribute('aria-pressed',String(g.group_id===state.selectedGroup));button.onclick=()=>controller.select(g.group_id);list.append(button);
  }
  const g=state.data?.groups.find(g=>g.group_id===state.selectedGroup);
  if(g){
   details.append(el('h3',g.designation),el('p',`Revisão ${g.composition_revision} · ${g.domain==='aereo'?'Aéreo':'Naval'} · posições de planejamento atuais`));
   const members=el('ul');
   for(const m of g.members){
    const li=el('li'),button=el('button',`${m.code} · ${m.name}`);button.type='button';
    button.dataset.groupFocus='member:'+m.asset_id;
    button.onclick=()=>controller.inspectMember(m.asset_id);li.append(button,el('span',m.latitude===null?' · Sem posição':' · Plotado'));
    if(m.reason)li.append(el('small',' · '+m.reason));members.append(li);
   }
   details.append(members);
   if(g.unavailable_count)details.append(el('p',`${g.unavailable_count} integrante(s): vínculo indisponível. Atualize a composição.`));
   details.append(el('p','Estado operativo e recursos: não avaliados nesta consulta.'));
   const fit=el('button','Enquadrar integrantes');fit.type='button';fit.disabled=!g.members.some(m=>m.latitude!==null&&m.longitude!==null);
   fit.dataset.groupFocus='fit';
   fit.onclick=()=>controller.focusSelected();details.append(fit);
   if(g.active&&archivePending===g.group_id){const confirmation=el('div');confirmation.setAttribute('role','group');confirmation.setAttribute('aria-label','Confirmar arquivamento');
    const accept=el('button','Confirmar arquivamento'),cancel=el('button','Cancelar arquivamento');accept.type=cancel.type='button';
    cancel.dataset.groupFocus='archive:'+g.group_id;
    accept.dataset.groupFocus='confirm-archive';accept.onclick=()=>{archivePending=null;controller.archive(g.group_id);};
    cancel.onclick=()=>{archivePending=null;desiredFocus='archive:'+g.group_id;render(current);};
    confirmation.append(el('p','Arquivar este grupamento? Os meios e suas posições serão preservados.'),accept,cancel);details.append(confirmation);
   }else if(g.active){const archive=el('button','Arquivar grupamento');archive.type='button';archive.disabled=state.busy||!state.data.exercise_open;
    archive.dataset.groupFocus='archive:'+g.group_id;
    archive.onclick=()=>{archivePending=g.group_id;render(current);details.querySelector('[data-group-focus="confirm-archive"]').focus();};details.append(archive);}
  }
  const member=state.data?.units.find(u=>u.asset_id===state.selectedMember);
  if(member){const section=el('section');section.setAttribute('aria-label','Consulta do meio selecionado');
   section.append(el('h3',member.code+' · '+member.name),el('p',member.unit_id?'ID da unidade: '+member.unit_id:'Instância não disponível.'),
    el('p',member.latitude===null?'Sem posição.':`Latitude ${member.latitude}° · Longitude ${member.longitude}° · revisão ${member.position_revision}`),
    el('p',member.reason||'Identidade elegível para composição; capacidade operacional não avaliada.'));details.append(section);}
  choices.replaceChildren(legend);
  const units=state.data?.units||[],allowed=new Set(units.filter(u=>u.eligible&&!u.in_active_group&&u.domain===domain.value).map(u=>u.unit_id));
  for(const uid of selected)if(!allowed.has(uid))selected.delete(uid);
  for(const u of units){
   const label=el('label'),check=el('input');check.type='checkbox';check.value=u.unit_id||'';
   check.disabled=!allowed.has(u.unit_id)||state.busy||!state.data.exercise_open;check.checked=selected.has(u.unit_id);
   check.onchange=()=>{if(check.checked)selected.add(u.unit_id);else selected.delete(u.unit_id);submit.disabled=!selected.size;};
   label.append(check,document.createTextNode(`${u.code} · ${u.name}`));
   if(u.reason||u.in_active_group)label.append(el('small',' · '+(u.reason||'Já integra um grupo ativo.')));choices.append(label);
  }
  if(state.data&&!units.length)choices.append(el('p','Nenhum meio adjudicado disponível.'));
  designation.disabled=domain.disabled=state.busy||!state.data?.exercise_open;
  submit.disabled=state.busy||!state.data?.exercise_open||!selected.size;
  if(desiredFocus){const nodes=[...container.querySelectorAll('[data-group-focus]')];
   const target=nodes.find(n=>n.dataset.groupFocus===desiredFocus&&!n.disabled)||
    (state.selectedGroup&&nodes.find(n=>n.dataset.groupFocus==='group:'+state.selectedGroup));
   target?.focus({preventScroll:true});}
 }
 const request=async(path,options)=>{
  const response=await fetch(path,options?{method:options.method,headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(options.body)}:undefined);
  const body=await response.json();if(!response.ok)throw Error(body.error||'Não foi possível consultar grupamentos.');return body;
 };
 const controller=createGroupController({request,render,highlight,focus});
 refresh.onclick=()=>controller.load(current.team);domain.onchange=()=>{selected.clear();render(current);};
 form.onsubmit=async event=>{event.preventDefault();if(!selected.size)return;await controller.create({designation:designation.value,domain:domain.value,member_unit_ids:[...selected]});};
 return controller;
}
