function renderFuelLimits(parent,runtime,reload) {
  const panel=el('section',{class:'fuel-limits','aria-label':'Alertas de combustível'}),labels={not_configured:'Mínimo não configurado',above_minimum:'Acima do mínimo',at_minimum:'Nível mínimo atingido',below_minimum:'Combustível abaixo do mínimo'};parent.append(panel);
  panel.append(el('h3',{text:'Nível mínimo de combustível'}),el('p',{class:'muted',text:'Operador do próprio partido e instrutor podem definir o mínimo por meio. Alerta ao atingir ou ficar abaixo do limite; não bloqueia consumo.'}));
  const displays=new Map(),format=n=>new Intl.NumberFormat('pt-BR',{maximumFractionDigits:3}).format(n);
  const update=(node,state)=>{const limit=state.minimum_alert;if(!limit)return;node.className=limit.active||limit.fuel_exhausted?'notice error':'notice';node.setAttribute('role',limit.active||limit.fuel_exhausted?'alert':'status');node.textContent=`${limit.fuel_exhausted?'Combustível esgotado. ':''}${labels[limit.status]} · saldo conferido ${format(state.fuel_remaining_kg)} kg${limit.minimum_grams===null?'':` · mínimo ${format(limit.minimum_grams/1000)} kg`} · versão ${limit.version}`;};
  for(const state of runtime.states){
    const policy=state.minimum_alert,card=el('article',{class:'compiled-component','data-limit-unit':state.unit_id}),status=el('p'),form=el('form'),id='fuel-min-'+state.unit_id,input=el('input',{id,type:'number',min:'0',step:'0.001',required:'required',value:policy.minimum_grams===null?'':String(policy.minimum_grams/1000)}),save=el('button',{class:'btn btn-secondary',type:'submit',text:'Salvar mínimo'}),clear=el('button',{class:'btn btn-secondary',type:'button',text:'Desativar alerta'}),message=el('p',{role:'status'});let pending=null;
    card.append(el('h4',{text:state.code}),status);update(status,state);displays.set(state.unit_id,status);
    const submit=async value=>{save.disabled=true;clear.disabled=true;if(!pending)pending={command_id:crypto.randomUUID(),run_id:runtime.run_id,unit_id:state.unit_id,expected_revision:runtime.revision,expected_limit_revision:policy.version,minimum_kg:value};
      try{await api('/api/engine-fuel-limit',pending);await reload();}catch(error){input.disabled=true;save.type='button';save.onclick=()=>submit(null);save.textContent='Repetir gravação';save.disabled=false;message.textContent=error.message+' Use Atualizar estado antes de uma nova alteração.';}
    };
    form.addEventListener('submit',event=>{event.preventDefault();submit(input.value);});clear.addEventListener('click',()=>submit(null));
    form.append(el('label',{class:'label',for:id,text:`Mínimo de ${state.code} (kg)`}),input,el('div',{class:'actions'},[save,clear]),message);card.append(form);panel.append(card);
  }
  const note=el('p',{class:'muted',role:'status',text:'Alertas conferidos ao atualizar e a cada 10 s enquanto este painel estiver aberto.'});panel.append(note);
  const timer=setInterval(async()=>{
    if(!panel.isConnected){clearInterval(timer);return;}
    if(document.hidden||!panel.closest('.engine-units-panel')?.open)return;
    try{const latest=await api('/api/engine-runtime'),visible=new Set(latest.states.map(state=>state.unit_id));for(const [id,node] of displays)node.closest('article').hidden=!visible.has(id);for(const state of latest.states){const node=displays.get(state.unit_id);if(node)update(node,state);}note.textContent='Alertas conferidos às '+new Date().toLocaleTimeString('pt-BR')+'.';}
    catch(error){note.textContent='Falha na atualização dos alertas. O último estado exibido pode estar desatualizado.';}
  },10000);
}
