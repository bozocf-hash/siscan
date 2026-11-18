// Conferência e ensaio sintético transitório: nunca publica efeitos oficiais.
export function createReadinessController({request,render,onForbidden=()=>{},confirmDiscard=()=>true}){
 const blank=()=>({preparation:null,hypotheses:null,result:null,trial:null,trialBusy:false,busy:false,dirty:false,error:'',invalid:false});let s=blank(),generation=0,formGeneration=0;
 const emit=()=>render(structuredClone(s));
 const invalidate=()=>{++generation;s.result=null;s.trial=null;s.trialBusy=false;s.busy=false;s.error='';emit();};
 const api={
  setPreparation(p){++generation;s={...blank(),formVersion:++formGeneration};s.preparation=p?structuredClone(p):null;emit();},
  edit(value){s.hypotheses=structuredClone(value);s.invalid=false;s.dirty=true;invalidate();},invalidate,
  inputError(message){++generation;s.result=null;s.trial=null;s.trialBusy=false;s.busy=false;s.dirty=true;s.invalid=true;s.error=message;emit();},
  editPolicy(){++generation;s.trial=null;s.trialBusy=false;s.busy=false;s.error='';s.dirty=true;emit();},
  canLeave(){if(s.dirty&&!confirmDiscard('As hipóteses são transitórias. Descartar a edição e sair?'))return false;const p=s.preparation;api.setPreparation(p);return true;},
  async check(){
   if(!s.preparation||s.busy||s.invalid)return false;const p=s.preparation,token=++generation;s.busy=true;s.error='';s.result=null;s.trial=null;s.trialBusy=false;emit();
   const body={selection:Object.fromEntries(p.parties.map(t=>[t.team,{group_id:t.group_id,expected_revision:t.composition_revision}])),expected_view_sha256:p.view_sha256};
   if(s.hypotheses!==null)body.hypotheses=structuredClone(s.hypotheses);
   try{
    const value=await request('/api/cpc/trial-readiness',{body});if(token!==generation)return false;
    if(value.schema_version!=='siscan-cpc-trial-readiness-01'||value.exercise_id!==p.exercise_id||value.scenario_version!==p.scenario_version||value.view_sha256!==p.view_sha256||value.official_calculation_ready!==false||value.simulation_started!==false||value.official_effects_applied!==false||typeof value.ready_for_controlled_trial!=='boolean'||!['units','excluded','issues','warnings'].every(k=>Array.isArray(value[k]))||value.ready_for_controlled_trial&&value.issues.length)throw Error('A resposta não corresponde ao par e ao contrato de prontidão.');
    s.result=value;s.busy=false;emit();return true;
   }catch(e){if(token===generation){if([401,403].includes(e.status)){s=blank();onForbidden();}s.error=e.message;s.busy=false;emit();}return false;}
  },
  async runTrial(policy){
   if(!s.result?.ready_for_controlled_trial||!s.hypotheses||s.busy||s.trialBusy||s.invalid)return false;
   const basis=structuredClone(s.result),p=s.preparation,selected=structuredClone(policy),token=++generation;
   s.trial=null;s.trialBusy=true;s.error='';emit();
   const body={selection:Object.fromEntries(p.parties.map(t=>[t.team,{group_id:t.group_id,expected_revision:t.composition_revision}])),expected_view_sha256:p.view_sha256,expected_basis_sha256:basis.basis_sha256,expected_hypotheses_sha256:basis.hypotheses_sha256,hypotheses:structuredClone(s.hypotheses),policy:selected};
   try{
    const value=await request('/api/cpc/controlled-trial',{body});if(token!==generation)return false;
    const returned=value.metadata?.policy;
    if(value.schema_version!=='siscan-cpc-controlled-trial-01'||value.exercise_id!==p.exercise_id||value.scenario_version!==p.scenario_version||value.view_sha256!==p.view_sha256||value.basis_sha256!==basis.basis_sha256||value.hypotheses_sha256!==basis.hypotheses_sha256||value.official_effects_applied!==false||value.simulation_started!==true||!['initial','final','events'].every(k=>Array.isArray(value[k]))||!Number.isInteger(value.minutes_completed)||value.minutes_completed<1||value.minutes_completed>120||!returned||returned.schema_version!==selected.schema_version||returned.initiative!==selected.initiative||!returned.weapons||Object.keys(returned.weapons).length!==Object.keys(selected.weapons).length||Object.keys(selected.weapons).some(k=>returned.weapons[k]!==selected.weapons[k]))throw Error('O resultado não corresponde às entradas conferidas do ensaio.');
    s.trial=value;s.trialBusy=false;emit();return true;
   }catch(e){if(token===generation){if([401,403].includes(e.status)){s=blank();onForbidden();}s.error=e.message;s.trialBusy=false;emit();}return false;}
  }
 };return api;
}
export function hypothesisDatum(raw,spec,acknowledged){
 if(raw.trim()==='')return undefined;let value=raw.trim();
 if(spec.kind==='boolean'){if(!['true','false'].includes(value))throw Error('Escolha uma disponibilidade válida.');value=value==='true';}
 else if(['number','integer'].includes(spec.kind)){value=Number(value);if(!Number.isFinite(value)||spec.kind==='integer'&&!Number.isSafeInteger(value))throw Error(spec.label||'Número inválido');}
 return {value,unit:spec.unit,...(acknowledged?{source:'didactic_assumption'}:{})};
}
export function installReadinessPanel({container,csrf,onBack,onForbidden}){
 const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
 container.classList.add('siscan-readiness');
 const heading=el('h3','Prontidão das entradas'),notice=el('p'),error=el('p'),summary=el('div'),form=el('details'),
  check=el('button','Conferir entradas'),back=el('button','Voltar ao julgamento');
 heading.tabIndex=-1;notice.setAttribute('role','status');error.setAttribute('role','alert');error.className='siscan-group-error';check.type=back.type='button';
 form.append(el('summary','Definir hipóteses do ensaio'));form.hidden=true;
 const trialArea=el('section'),trialControls=el('details'),trialSummary=el('div'),trialNotice=el('p');trialArea.hidden=true;trialNotice.setAttribute('role','status');trialArea.append(trialNotice,trialControls,trialSummary);
 container.append(heading,el('small','Hipóteses e ensaios didáticos separados do estado oficial.'),notice,error,summary,form,trialArea,check,back);
 let controller,formKey=null,formData=null,lookup=new Map(),wasBusy=false,trialKey=null,trialInputs=null;
 const button=(text,host,action)=>{const b=el('button',text);b.type='button';b.onclick=action;host.append(b);return b;};
 function section(host,title){const d=el('details');d.append(el('summary',title));d.ontoggle=()=>{if(d.open)for(const other of host.children)if(other!==d&&other.tagName==='DETAILS')other.open=false;};host.append(d);return d;}
 function field(host,spec,label=spec.label){
  const l=el('label',label+(spec.unit&&!['1','state','scale','local'].includes(spec.unit)?' ('+spec.unit+')':'')),input=el(['boolean','flight'].includes(spec.kind)?'select':'input');
  input.setAttribute('aria-label',label);
  if(input.tagName==='SELECT')for(const [value,text] of [['','Selecionar…'],...(spec.kind==='boolean'?[['true','Disponível para o ensaio'],['false','Indisponível']]:[['em_voo','Em voo'],['evadindo','Evadindo'],['pousado','Pousado'],['perda_proposta','Perda proposta no ensaio']])]){const o=el('option',text);o.value=value;input.append(o);}
  else {input.type=['integer','number'].includes(spec.kind)?'number':'text';input.step=spec.kind==='integer'?'1':'any';if(spec.minimum!==null&&spec.minimum!==undefined)input.min=spec.minimum;if(spec.maximum!==null&&spec.maximum!==undefined)input.max=spec.maximum;if(input.type==='text')input.maxLength=200;}
  input.oninput=input.onchange=capture;l.append(input);host.append(l);return {input,spec};
 }
 function descriptor(f){return hypothesisDatum(f.input.value,f.spec,formData.ack.checked);}
 function capture(){
  if(!formData)return;
  try{
   const data=formData,h={schema_version:data.schema,label:data.label.input.value,scenario:{},units:[]};
   if(data.revision.input.value.trim()!==''){const n=Number(data.revision.input.value);if(!Number.isSafeInteger(n)||n<1)throw Error('Informe revisão inteira positiva.');h.revision=n;}
   for(const [key,f] of data.scenario){const d=descriptor(f);if(d!==undefined)h.scenario[key]=d;}
   if(data.factors.length)h.scenario.fatores_assinatura=data.factors.map(r=>Object.fromEntries(Object.entries(r.fields).map(([k,f])=>[k,descriptor(f)]).filter(([,v])=>v!==undefined)));
   for(const u of data.units){const entry={unit_id:u.unit_id,parameters:{}};for(const [key,f] of u.fields){const d=descriptor(f);if(d!==undefined)entry.parameters[key]=d;}
    if(u.empty.checked)entry.armamentos=[];
    else if(u.stocks.length)entry.armamentos=u.stocks.map(r=>{const w={estoque_id:r.id};if(r.type.value)w.tipo=r.type.value;for(const [key,f] of r.fields){const d=descriptor(f);if(d!==undefined)w[key]=d;}return w;});h.units.push(entry);
   }
   controller.edit(h);
  }catch(e){controller.inputError(e.message);}
 }
 function buildForm(result){
  formData=null;lookup.clear();while(form.children.length>1)form.lastChild.remove();
  const data={schema:result.requirements.profile_schema,scenario:new Map(),units:[],factors:[]};
  const ack=el('input');ack.type='checkbox';ack.setAttribute('aria-label','Confirmar hipóteses didáticas');const ackLabel=el('label',' Declaro os valores preenchidos como hipóteses didáticas.');ackLabel.prepend(ack);ack.onchange=capture;data.ack=ack;form.append(ackLabel,el('small','Valores transitórios, sem alterar o estado oficial ou aprovar dados Command.'));
  const scenario=section(form,'Identificação e cenário');data.label=field(scenario,{kind:'text'},'Nome das hipóteses');data.revision=field(scenario,{kind:'integer',minimum:1},'Revisão das hipóteses');lookup.set('|label',data.label.input);lookup.set('|revision',data.revision.input);
  for(const spec of result.requirements.scenario){const f=field(scenario,spec);data.scenario.set(spec.key,f);lookup.set('|scenario.'+spec.key,f.input);}
  const factors=section(form,'Fatores didáticos de assinatura'),factorsList=el('div');factors.append(el('small','Declare um fator por valor de assinatura; não há interpolação.'),factorsList);
  button('Adicionar fator de assinatura',factors,()=>{
   const row={fields:{}},box=el('fieldset'),n=data.factors.length+1;
   row.fields.assinatura_radar=field(box,{kind:'number',unit:'m2',minimum:0},'Assinatura do fator · '+n);
   row.fields.fator=field(box,{kind:'number',unit:'1',minimum:0,maximum:1},'Fator de assinatura · '+n);
   button('Remover fator',box,()=>{data.factors=data.factors.filter(x=>x!==row);box.remove();capture();});factorsList.append(box);data.factors.push(row);capture();
  });lookup.set('|scenario.fatores_assinatura',factors);
  for(const unit of result.units){
   const box=el('fieldset');box.append(el('legend',unit.team+' · '+unit.code));form.append(box);
   const u={unit_id:unit.unit_id,fields:new Map(),stocks:[],serial:0},sections=new Map();
   for(const spec of result.requirements.units[unit.unit_id]||[]){if(!sections.has(spec.section))sections.set(spec.section,section(box,spec.section));const f=field(sections.get(spec.section),spec,spec.label+' · '+unit.code);u.fields.set(spec.key,f);lookup.set(unit.unit_id+'|'+spec.key,f.input);}
   const weapons=section(box,'Armamentos'),empty=el('input');empty.type='checkbox';empty.setAttribute('aria-label','Sem armamento no ensaio · '+unit.code);const emptyLabel=el('label',' Sem armamento neste ensaio');emptyLabel.prepend(empty);weapons.append(emptyLabel);u.empty=empty;
   const stockList=el('div');weapons.append(stockList);
   const add=button('Adicionar estoque · '+unit.code,weapons,()=>{
    const row={id:unit.unit_id+'-hipotese-'+(++u.serial),fields:new Map()},stock=el('fieldset');stock.append(el('legend','Estoque hipotético '+u.serial));
    const typeLabel=el('label','Tipo'),type=el('select');type.setAttribute('aria-label','Tipo de armamento · '+unit.code+' · Estoque '+u.serial);row.type=type;
    for(const [value,text] of [['','Selecionar…'],['missil_ar_ar','Míssil ar-ar'],['missil_antinavio','Míssil antinavio'],['defesa_ponto','Defesa de ponto']]){const o=el('option',text);o.value=value;type.append(o);}type.onchange=capture;typeLabel.append(type);stock.append(typeLabel);
    for(const spec of result.requirements.weapons)row.fields.set(spec.key,field(stock,spec,spec.label+' · '+unit.code+' · Estoque '+u.serial));
    button('Remover estoque',stock,()=>{u.stocks=u.stocks.filter(x=>x!==row);stock.remove();capture();});stockList.append(stock);u.stocks.push(row);capture();
   });
   empty.onchange=()=>{stockList.hidden=empty.checked;add.disabled=empty.checked;capture();};lookup.set(unit.unit_id+'|armamentos',weapons);data.units.push(u);
  }
  formData=data;form.hidden=false;
 }
 function focusIssue(i){
  form.open=true;let node=lookup.get((i.unit_id||'')+'|'+i.field);
  if(!node&&i.field.includes('fatores_assinatura'))node=lookup.get('|scenario.fatores_assinatura');
  if(!node&&i.field.startsWith('armamentos'))node=lookup.get(i.unit_id+'|armamentos');
  if(node){for(let p=node;p&&p!==form;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;node.focus();node.scrollIntoView({block:'nearest'});}
 }
 function showTrial(s){
  trialArea.hidden=!s.result?.ready_for_controlled_trial;
  if(trialArea.hidden){trialKey=null;trialInputs=null;trialControls.replaceChildren();trialSummary.replaceChildren();return;}
  const key=s.result.basis_sha256+'|'+s.result.hypotheses_sha256;
  if(key!==trialKey){
   trialKey=key;trialControls.replaceChildren(el('summary','Configurar ensaio controlado'));trialInputs={weapons:new Map()};
   trialControls.append(el('small','Uma tentativa por minuto com o estoque escolhido. Até 120 min; encerra na primeira perda. Geometria local hipotética.'));
   const orderLabel=el('label','Ordem das ações'),order=el('select');order.setAttribute('aria-label','Ordem das ações do ensaio');
   for(const [v,t] of [['','Selecionar…'],['simultaneous','Simultâneas'],['AZUL','Iniciativa AZUL'],['VERMELHO','Iniciativa VERMELHO']]){const o=el('option',t);o.value=v;order.append(o);}order.onchange=()=>controller.editPolicy();orderLabel.append(order);trialControls.append(orderLabel);trialInputs.order=order;
   for(const unit of s.result.units){
    const label=el('label',unit.team+' · '+unit.code),select=el('select');select.setAttribute('aria-label','Estoque do ensaio · '+unit.code);
    const options=[['','Selecionar…'],['none','Nenhuma ação ofensiva'],...(s.hypotheses.units.find(u=>u.unit_id===unit.unit_id)?.armamentos||[]).filter(w=>w.tipo==='missil_ar_ar').map((w,i)=>[w.estoque_id,'Estoque ar-ar '+(i+1)+' · '+w.quantidade.value+' itens'])];
    for(const [v,t] of options){const o=el('option',t);o.value=v;select.append(o);}select.onchange=()=>controller.editPolicy();label.append(select);trialControls.append(label);trialInputs.weapons.set(unit.unit_id,select);
   }
   trialInputs.run=button('Executar ensaio controlado',trialControls,()=>controller.runTrial({schema_version:'siscan-cpc-controlled-policy-01',initiative:trialInputs.order.value,weapons:Object.fromEntries([...trialInputs.weapons].map(([id,input])=>[id,input.value==='none'?null:input.value]))}));
   trialControls.open=true;
  }
  trialInputs.run.disabled=s.trialBusy||!trialInputs.order.value||[...trialInputs.weapons.values()].some(i=>!i.value);
  for(const input of [trialInputs.order,...trialInputs.weapons.values()])input.disabled=s.trialBusy;
  trialNotice.textContent=s.trialBusy?'Executando ensaio sintético…':s.trial?'Ensaio encerrado · sem efeitos oficiais':'Execução opcional; confira a política antes de iniciar.';
  trialSummary.replaceChildren();
  if(!s.trial)return;
  const r=s.trial;trialControls.open=false;trialSummary.append(el('h4','Resultado sugerido do ensaio'),el('p',r.minutes_completed+' de '+r.minutes_requested+' min · '+(r.stop_reason==='participant_loss'?'encerrado por perda proposta':'duração concluída')));
  for(const final of r.final){
   const initial=r.initial.find(u=>u.unidade_id===final.unidade_id),unit=r.units.find(u=>u.unit_id===final.unidade_id),d=el('details');
   d.append(el('summary',unit.team+' · '+unit.code+' · '+(r.balance.perdas_propostas.includes(final.unidade_id)?'perda proposta':({em_voo:'em voo',evadindo:'evadindo',pousado:'pousado'})[final.estado_voo])),
    el('p','Vida: '+initial.pontos_de_vida+' → '+final.pontos_de_vida+' pontos'),el('p','Combustível: '+initial.combustivel_kg+' → '+final.combustivel_kg+' kg'));
   for(const [i,stock] of final.armamentos.entries()){const before=initial.armamentos.find(w=>w.estoque_id===stock.estoque_id);d.append(el('p','Estoque hipotético '+(i+1)+': '+before.quantidade+' → '+stock.quantidade+' itens'));}trialSummary.append(d);
  }
  trialSummary.append(el('p','Perdas propostas: '+r.balance.quantidade_perdas_propostas+' · mísseis gastos: '+r.balance.misseis_gastos));
  const events=el('details');events.append(el('summary','Histórico · '+r.events.length+' eventos'));
  for(const e of r.events.slice(0,100))events.append(el('p',e.minuto+' min · '+e.tipo+(e.unidade_id?' · '+(r.units.find(u=>u.unit_id===e.unidade_id)?.code||e.unidade_id):'')));
  if(r.events.length>100)events.append(el('small','Exibidos os primeiros 100 eventos. O JSON inclui o histórico completo.'));trialSummary.append(events);
  button('Baixar relatório JSON',trialSummary,()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(r,null,2)],{type:'application/json'})),a=el('a');a.href=url;a.download='ensaio-cpc-'+r.metadata.execucao_id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  trialSummary.append(el('small','A decisão continua com o instrutor. Pontos do ensaio não são índice operativo oficial.'));
 }
 controller=createReadinessController({request:async(path,options)=>{
  const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),15000);
  try{const response=await fetch(path,{method:'POST',signal:abort.signal,headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(options.body)});const data=await response.json();if(!response.ok)throw Object.assign(Error(data.error||'Prontidão indisponível.'),{status:response.status});return data;}finally{clearTimeout(timer);}
 },onForbidden,confirmDiscard:message=>window.confirm(message),render:s=>{
  const completed=wasBusy&&!(s.busy||s.trialBusy);wasBusy=s.busy||s.trialBusy;
  const key=s.preparation?s.preparation.view_sha256+'|'+s.formVersion:null;if(key!==formKey){formKey=key;formData=null;lookup.clear();while(form.children.length>1)form.lastChild.remove();form.hidden=true;}
  check.disabled=s.busy||s.trialBusy||!s.preparation||s.invalid;notice.textContent=s.busy?'Conferindo fontes…':s.result?({incomplete:'Entradas incompletas',unsupported:'Recorte não suportado',ready:'Entradas prontas para ensaio controlado'})[s.result.status]:s.dirty?'Hipóteses alteradas · conferir novamente.':'Confira as entradas do par preparado.';notice.className='readiness-status';notice.dataset.state=s.result?.status||'';error.textContent=s.error;summary.replaceChildren();
  if(s.result){
   if(!formData&&s.result.requirements)buildForm(s.result);
   const group=(title,items)=>{if(!items.length)return;const d=el('details');d.append(el('summary',title+' · '+items.length+(title==='Avisos'?'':items.length===1?' pendência':' pendências')));for(const i of items){const p=el('p',i.message);d.append(p,el('small',i.action));if(i.category==='missing_data'||i.code==='missing_signature_factor')button('Ver campo',d,()=>focusIssue(i));}summary.append(d);};
   for(const unit of s.result.units)group(unit.team+' · '+unit.code,s.result.issues.filter(i=>i.unit_id===unit.unit_id));group('Cenário',s.result.issues.filter(i=>!i.unit_id));group('Avisos',s.result.warnings);for(const u of s.result.excluded)summary.append(el('p',u.code+' · '+u.reason));
   if(s.result.ready_for_controlled_trial){summary.append(el('p','Entradas consistentes para o recorte controlado.'));if(completed){form.open=false;container.parentElement.scrollTop=0;}}
  }
  showTrial(s);
  if(completed&&document.activeElement===document.body)heading.focus({preventScroll:true});
 }});
 check.onclick=()=>controller.check();back.onclick=()=>{if(controller.canLeave())onBack();};return controller;
}
