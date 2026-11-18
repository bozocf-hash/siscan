// Consulta de entradas: não executa combate nem publica efeitos.
export function createReadinessController({request,render,onForbidden=()=>{},confirmDiscard=()=>true}){
 const blank=()=>({preparation:null,hypotheses:null,result:null,busy:false,dirty:false,error:'',invalid:false});let s=blank(),generation=0,formGeneration=0;
 const emit=()=>render(structuredClone(s));
 const invalidate=()=>{++generation;s.result=null;s.busy=false;s.error='';emit();};
 const api={
  setPreparation(p){++generation;s={...blank(),formVersion:++formGeneration};s.preparation=p?structuredClone(p):null;emit();},
  edit(value){s.hypotheses=structuredClone(value);s.invalid=false;s.dirty=true;invalidate();},invalidate,
  inputError(message){++generation;s.result=null;s.busy=false;s.dirty=true;s.invalid=true;s.error=message;emit();},
  canLeave(){if(s.dirty&&!confirmDiscard('As hipóteses são transitórias. Descartar a edição e sair?'))return false;const p=s.preparation;api.setPreparation(p);return true;},
  async check(){
   if(!s.preparation||s.busy||s.invalid)return false;const p=s.preparation,token=++generation;s.busy=true;s.error='';s.result=null;emit();
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
 container.append(heading,el('small','Conferência didática. Não executa combate nem aplica resultado.'),notice,error,summary,form,check,back);
 let controller,formKey=null,formData=null,lookup=new Map(),wasBusy=false;
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
 controller=createReadinessController({request:async(path,options)=>{
  const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),15000);
  try{const response=await fetch(path,{method:'POST',signal:abort.signal,headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(options.body)});const data=await response.json();if(!response.ok)throw Object.assign(Error(data.error||'Prontidão indisponível.'),{status:response.status});return data;}finally{clearTimeout(timer);}
 },onForbidden,confirmDiscard:message=>window.confirm(message),render:s=>{
  const completed=wasBusy&&!s.busy;wasBusy=s.busy;
  const key=s.preparation?s.preparation.view_sha256+'|'+s.formVersion:null;if(key!==formKey){formKey=key;formData=null;lookup.clear();while(form.children.length>1)form.lastChild.remove();form.hidden=true;}
  check.disabled=s.busy||!s.preparation||s.invalid;notice.textContent=s.busy?'Conferindo fontes…':s.result?({incomplete:'Entradas incompletas',unsupported:'Recorte não suportado',ready:'Entradas prontas para ensaio controlado'})[s.result.status]:s.dirty?'Hipóteses alteradas · conferir novamente.':'Confira as entradas do par preparado.';notice.className='readiness-status';notice.dataset.state=s.result?.status||'';error.textContent=s.error;summary.replaceChildren();
  if(s.result){
   if(!formData&&s.result.requirements)buildForm(s.result);
   const group=(title,items)=>{if(!items.length)return;const d=el('details');d.append(el('summary',title+' · '+items.length+(title==='Avisos'?' avisos':' pendências')));for(const i of items){const p=el('p',i.message);d.append(p,el('small',i.action));if(i.category==='missing_data'||i.code==='missing_signature_factor')button('Ver campo',d,()=>focusIssue(i));}summary.append(d);};
   for(const unit of s.result.units)group(unit.team+' · '+unit.code,s.result.issues.filter(i=>i.unit_id===unit.unit_id));group('Cenário',s.result.issues.filter(i=>!i.unit_id));group('Avisos',s.result.warnings);for(const u of s.result.excluded)summary.append(el('p',u.code+' · '+u.reason));
   if(s.result.ready_for_controlled_trial){summary.append(el('p','Entradas consistentes para o recorte controlado. Nenhum confronto foi executado.'));form.open=false;if(completed)container.parentElement.scrollTop=0;}
  }
  if(completed&&document.activeElement===document.body)heading.focus({preventScroll:true});
 }});
 check.onclick=()=>controller.check();back.onclick=()=>{if(controller.canLeave())onBack();};return controller;
}
