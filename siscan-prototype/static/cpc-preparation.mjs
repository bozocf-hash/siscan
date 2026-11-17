// Conferência de duas composições; sem execução ou publicação de resultados.
const TEAMS=['AZUL','VERMELHO'];
export function createCpcController({request,render,preview,beforeChange=()=>true}){
 let generation=0;
 const empty=active=>({active,list:null,selection:{AZUL:null,VERMELHO:null},preparation:null,member:null,loading:false,busy:false,error:''});
 let state=empty(false);
 const emit=()=>render(structuredClone(state));
 function clearView(){state.preparation=null;state.member=null;preview(null);}
 async function enter(){
  if(state.active&&!beforeChange())return false;
  const token=++generation;state=empty(true);state.loading=true;preview(null);emit();
  try{
   const data=await request('/api/cpc/groups');if(token!==generation)return;
   if(!Number.isInteger(data.exercise_id)||!Number.isInteger(data.scenario_version)||!Array.isArray(data.parties)||
      !TEAMS.every(t=>data.parties.some(p=>p.team===t&&Array.isArray(p.groups))))throw Error('Lista CPC inválida.');
   state.list=data;state.loading=false;emit();
  }catch(error){if(token===generation){state.list=null;state.loading=false;state.error=error.message;emit();}}
 }
 function choose(team,id){
  if(!TEAMS.includes(team)||!state.active)return;
  if(!beforeChange()){emit();return;}
  const group=state.list?.parties.find(p=>p.team===team)?.groups.find(g=>g.group_id===id&&g.preparable);
  ++generation;state.selection[team]=group?group.group_id:null;state.busy=false;clearView();state.error='';emit();
 }
 async function prepare(){
  if(!state.active||state.loading||state.busy||!state.list?.exercise_open)return false;
  if(!beforeChange())return false;
  const selection={};
  for(const team of TEAMS){
   const group=state.list.parties.find(p=>p.team===team).groups.find(g=>g.group_id===state.selection[team]&&g.preparable);
   if(!group){state.error='Selecione um grupamento disponível de cada partido.';emit();return false;}
   selection[team]={group_id:group.group_id,expected_revision:group.composition_revision};
  }
  const token=++generation,context=state.list;state.busy=true;state.error='';clearView();emit();
  try{
   const result=await request('/api/cpc/preparations',{method:'POST',body:selection});if(token!==generation)return false;
   if(result.exercise_id!==context.exercise_id||result.scenario_version!==context.scenario_version)throw Error('O contexto/cenário mudou. Atualize os grupos.');
   if(result.schema_version!=='siscan-cpc-map-preparation-01'||result.simulation_started!==false||
      result.official_calculation_ready!==false||result.official_effects_applied!==false||!Array.isArray(result.parties)||
      result.parties.length!==2||!TEAMS.every(t=>result.parties.some(p=>p.team===t&&p.group_id===selection[t].group_id&&
        p.composition_revision===selection[t].expected_revision&&Array.isArray(p.members))))throw Error('A preparação devolvida não corresponde ao par selecionado.');
   state.preparation=result;state.busy=false;preview(structuredClone(result));emit();return true;
  }catch(error){if(token===generation){clearView();state.busy=false;state.list=null;state.selection={AZUL:null,VERMELHO:null};state.error=error.message;emit();}return false;}
 }
 return {enter,choose,prepare,
  restore(preparation){
   if(!state.active||!state.list||preparation.exercise_id!==state.list.exercise_id||preparation.scenario_version!==state.list.scenario_version)return false;
   if(!TEAMS.every(team=>{const p=preparation.parties.find(x=>x.team===team);return p&&state.list.parties.find(x=>x.team===team)?.groups.some(g=>g.preparable&&g.group_id===p.group_id&&g.composition_revision===p.composition_revision);}))return false;
   ++generation;state.selection=Object.fromEntries(preparation.parties.map(p=>[p.team,p.group_id]));state.preparation=structuredClone(preparation);state.member=null;state.error='';preview(structuredClone(preparation));emit();return true;
  },
  leave:()=>{++generation;state=empty(false);preview(null);emit();},
  inspect:uid=>{const exists=state.preparation?.parties.some(p=>p.members.some(m=>m.unit_id===uid));state.member=exists?uid:null;emit();}};
}

export function installCpcPanel({container,csrf,preview,focus,exit,installJudgmentPanel=null,onOfficial=()=>{}}){
 const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
 const heading=el('h2','Preparação CPC'),note=el('p','Conferência do par: não executa combate nem aplica resultados.'),
  warning=el('p','Grupos temporários; dados confirmados nesta vista não reservam disponibilidade futura.'),
  status=el('p'),selectors=el('div'),prepareButton=el('button','Preparar confronto'),refresh=el('button','Atualizar grupos CPC'),
  back=el('button','Voltar ao planejamento'),fit=el('button','Enquadrar o par'),details=el('div');
 warning.className='siscan-group-warning';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 const selects={};
 for(const team of TEAMS){const label=el('label','Grupamento '+team),select=el('select');select.setAttribute('aria-label','Grupamento '+team);label.append(select);selectors.append(label);selects[team]=select;}
 for(const button of [prepareButton,refresh,back,fit])button.type='button';
 container.append(heading,note,warning,status,selectors,prepareButton,refresh,back,fit,details);
 const judgmentArea=el('section');container.append(judgmentArea);let judgment=null,lastPreparation,restoring=false,officialConsulted=false;
 let wasBusy=false,restorePreparationFocus=false;
 function render(state){
  const preparationKey=state.preparation?.view_sha256??null;
  if(judgment&&(!state.active||preparationKey!==lastPreparation)){lastPreparation=preparationKey;officialConsulted=false;if(!restoring)judgment.setPreparation(state.preparation);}
  if(state.busy&&!wasBusy)restorePreparationFocus=document.activeElement===prepareButton;
  const completed=wasBusy&&!state.busy;wasBusy=state.busy;
  status.textContent=state.error||(state.loading?'Consultando composições…':state.busy?'Conferindo dados e posições…':state.preparation?officialConsulted?'Par conferido. Estado oficial consultado; julgamento no painel abaixo.':'Par conferido. Revisão do instrutor pendente.':state.list?`Exercício ${state.list.exercise_id} · cenário v${state.list.scenario_version}${state.list.exercise_open?'':' · Encerrado'}`:'Atualize os grupos para conferir.');
  status.className=state.error?'siscan-group-error':'';
  for(const team of TEAMS){
   const select=selects[team];select.replaceChildren();const initial=el('option','Selecione '+team);initial.value='';select.append(initial);
   for(const group of state.list?.parties.find(p=>p.team===team)?.groups||[]){const o=el('option',`${group.designation} · revisão ${group.composition_revision}${group.reason?' · '+group.reason:''}`);o.value=group.group_id;o.disabled=!group.preparable;select.append(o);}
   select.value=state.selection[team]||'';select.disabled=state.loading||!state.list;
  }
  prepareButton.disabled=state.loading||state.busy||!state.list?.exercise_open||!TEAMS.every(t=>state.selection[t]);
  fit.disabled=!state.preparation?.parties.some(p=>p.members.some(m=>m.latitude!==null&&m.longitude!==null));
  details.replaceChildren();
  if(state.preparation){
   for(const party of state.preparation.parties){
    const section=el('section');section.append(el('h3',`${party.team} · ${party.designation}`),el('p',`Revisão ${party.composition_revision} · ${party.domain==='aereo'?'Aéreo':'Naval'}`));
    const list=el('ul');
    for(const member of party.members){const li=el('li'),button=el('button',`${member.code} · ${member.name}`);button.type='button';button.dataset.cpcMember=member.unit_id;
     button.onclick=()=>controller.inspect(member.unit_id);li.append(button,el('small',member.latitude===null?'Sem posição':`Posição de planejamento: ${member.latitude}°, ${member.longitude}° · revisão ${member.position_revision}`));list.append(li);
     if(state.member===member.unit_id){const refs=el('details'),summary=el('summary','Referências da configuração inicial');refs.append(summary,el('p','Unidade: '+member.unit_id),el('p','Snapshot: '+member.snapshot_id),el('p','Configuração: '+member.configuration_version_id));li.append(refs,el('p','Estado logístico atual: não informado. Snapshot técnico inicial não é saldo atual.'));}
    }
    section.append(list);details.append(section);
   }
   const refs=el('details');refs.append(el('summary','Referências desta conferência'),el('p','Dossiê: '+state.preparation.dossier_sha256),el('p','Posições: '+state.preparation.positions_sha256),el('p','Vista: '+state.preparation.view_sha256));details.append(refs);
   if(!judgment)details.append(el('p','Julgamento indisponível nesta instância; atualize o servidor.'));
   if(state.member)details.querySelector(`[data-cpc-member="${CSS.escape(state.member)}"]`)?.focus({preventScroll:true});
  }
  if(completed){if(state.active&&restorePreparationFocus&&document.activeElement===document.body)(prepareButton.disabled?refresh:prepareButton).focus({preventScroll:true});restorePreparationFocus=false;}
 }
 const request=async(path,options)=>{const response=await fetch(path,options?{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(options.body)}:undefined);const body=await response.json();if(!response.ok)throw Object.assign(Error(body.error||'Conferência indisponível.'),{status:response.status});return body;};
 const controller=createCpcController({request,render,preview,beforeChange:()=>judgment?.canLeave()??true});
 if(installJudgmentPanel)judgment=installJudgmentPanel({container:judgmentArea,csrf,
  onOfficial:states=>{officialConsulted=true;status.textContent='Par conferido. Estado oficial consultado; julgamento no painel abaixo.';onOfficial(states);},
  onResumePair:preparation=>{restoring=true;try{return controller.restore(preparation);}finally{restoring=false;}},onForbidden:()=>controller.leave()});
 controller.canLeave=()=>judgment?.canLeave()??true;
 for(const team of TEAMS)selects[team].onchange=()=>controller.choose(team,selects[team].value);
 refresh.onclick=()=>controller.enter();prepareButton.onclick=()=>controller.prepare();back.onclick=exit;fit.onclick=focus;
 return controller;
}
