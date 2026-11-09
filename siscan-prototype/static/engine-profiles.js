function renderEngineProfile(parent,runtime) {
  const panel=el('details',{class:'equipment-group profile-panel','aria-label':'Previsão por perfil temporal'},[el('summary',{text:'Prever perfil de consumo'})]);parent.append(panel);
  panel.append(el('p',{class:'source-caveat',text:'Taxas hipotéticas de teste. Esta prévia não vem do Command, não substitui a taxa da execução constante e não debita combustível. O eixo de tempo começa no saldo atual.'}));
  const content=el('div');panel.append(content);let loaded=false;
  panel.addEventListener('toggle',async()=>{
    if(!panel.open||loaded)return;loaded=true;content.replaceChildren(el('p',{role:'status',text:'Conferindo contrato de perfis…'}));
    try{
      const contract=await api('/api/engine-profile-contract'),form=el('form'),units=el('select',{id:'profile-unit'}),rows=el('div',{class:'profile-segments'}),result=el('div',{'aria-live':'polite'});let counter=0,generation=0;
      for(const state of runtime.states)units.append(el('option',{value:state.unit_id,text:`${state.code} · saldo ${state.fuel_remaining_kg} kg`}));
      const format=value=>new Intl.NumberFormat('pt-BR',{maximumFractionDigits:3}).format(value);
      const invalidate=()=>{generation++;result.replaceChildren();};
      const add=el('button',{type:'button',class:'btn btn-secondary',text:'Adicionar trecho'}),calculate=el('button',{type:'submit',class:'btn',text:'Calcular previsão'});
      const refresh=()=>{const items=[...rows.children];add.disabled=items.length>=24;for(const item of items)item.querySelector('button').disabled=items.length===1;};
      const append=(regime='SYN-REF',minutes=10)=>{
        const id=++counter,row=el('div',{class:'profile-segment'}),select=el('select',{id:`profile-regime-${id}`}),time=el('input',{id:`profile-time-${id}`,type:'number',min:'1',max:'1440',step:'1',required:'required',value:String(minutes)});
        for(const r of contract.dataset.regimes){const option=el('option',{value:r.id,text:`${r.label} · ${format(r.grams_per_minute/1000)} kg/min`});option.selected=r.id===regime;select.append(option);}
        const remove=el('button',{type:'button',class:'btn btn-secondary',text:'Remover','aria-label':`Remover trecho ${id}`,onclick:()=>{row.remove();invalidate();refresh();}});
        row.append(el('div',{},[el('label',{class:'label',for:select.id,text:`Regime do trecho ${id}`}),select]),el('div',{},[el('label',{class:'label',for:time.id,text:`Minutos do trecho ${id}`}),time]),remove);rows.append(row);refresh();
      };
      form.addEventListener('input',invalidate);form.addEventListener('change',invalidate);
      add.addEventListener('click',()=>{if(rows.children.length<24){append();invalidate();}});
      form.append(el('label',{class:'label',for:'profile-unit',text:'Unidade para previsão'}),units,rows,el('div',{class:'actions'},[add,calculate]));
      append('SYN-ECO',10);append('SYN-REF',20);append('SYN-HIGH',5);
      if(!runtime.advance_allowed){calculate.disabled=true;form.append(el('p',{text:'Atualize a execução antes de calcular: cenário, versão ou estado incompatível.'}));}
      form.addEventListener('submit',async event=>{
        event.preventDefault();const revision=generation;calculate.disabled=true;result.replaceChildren(el('p',{role:'status',text:'Calculando previsão sem alterar saldos…'}));
        const payload={run_id:runtime.run_id,unit_id:units.value,expected_revision:runtime.revision,segments:[...rows.children].map(row=>({regime_id:row.querySelector('select').value,minutes:Number(row.querySelector('input').value)}))};
        try{
          const data=await api('/api/engine-profile-preview',payload);if(revision!==generation)return;result.replaceChildren();
          result.append(el('p',{class:data.feasible?'notice':'notice error',text:`${data.feasible?'Combustível suficiente nesta previsão.':'Combustível insuficiente nesta previsão.'} Demanda: ${format(data.fuel_required_grams/1000)} kg · saldo previsto: ${format(data.fuel_remaining_grams/1000)} kg · déficit: ${format(data.shortfall_grams/1000)} kg · duração: ${data.duration_minutes} min.`}));
          result.append(el('p',{class:'muted',text:`Base: ${data.basis_elapsed_minutes} min, revisão ${data.manifest.revision}. Previsão somente; saldo e relógio não foram alterados.`}),profileCurve(data));
          if(data.minimum_reached_at_offset_minutes!==null)result.append(el('p',{role:'alert',class:'notice error',text:`Mínimo de ${format(data.minimum_alert.minimum_grams/1000)} kg atingido em aproximadamente ${format(data.minimum_reached_at_offset_minutes)} min do perfil. Este alerta é distinto do esgotamento.`}));
          if(data.exhaustion_at_offset_minutes!==null)result.append(el('p',{text:`Esgotamento previsto após aproximadamente ${format(data.exhaustion_at_offset_minutes)} min do perfil. A demanda não atendida é contabilizada como déficit.`}));
          const table=el('table',{class:'technical-matrix'}),body=el('tbody');table.append(el('thead',{},[el('tr',{},['Trecho / regime','Duração (min)','Taxa (kg/min)','Demanda (kg)','Disponível (kg)','Déficit acumulado (kg)'].map(text=>el('th',{scope:'col',text})))]));
          data.segments.forEach((s,index)=>body.append(el('tr',{},[`${index+1} · ${s.label}`,s.minutes,format(s.rate_grams_per_minute/1000),format(s.fuel_required_grams/1000),format(s.available_grams/1000),format(s.shortfall_grams/1000)].map(text=>el('td',{text:String(text)})))));table.append(body);result.append(el('div',{class:'technical-table-scroll',tabindex:'0'},[table]));
          result.append(el('details',{class:'equipment-group'},[el('summary',{text:'Manifesto da previsão'}),el('pre',{class:'profile-manifest',text:JSON.stringify({...data.manifest,manifest_sha256:data.manifest_sha256},null,2)})]));
        }catch(error){if(revision===generation)result.replaceChildren(el('p',{role:'alert',class:'notice error',text:error.message}));}
        finally{calculate.disabled=!runtime.advance_allowed;}
      });content.replaceChildren(form,result);
    }catch(error){loaded=false;content.replaceChildren(el('p',{role:'alert',text:error.message}));}
  });
}

function profileCurve(data) {
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
  const shape=(tag,attrs,text)=>{const node=document.createElementNS(ns,tag);for(const [key,value] of Object.entries(attrs))node.setAttribute(key,String(value));if(text!==undefined)node.textContent=text;svg.append(node);return node;};
  svg.setAttribute('viewBox','0 0 540 230');svg.setAttribute('role','img');svg.setAttribute('aria-label','Curva prevista de combustível disponível em kg ao longo do perfil em minutos');svg.setAttribute('class','profile-curve');
  const minimum=data.minimum_alert?.minimum_grams,maximum=Math.max(1,data.fuel_basis_grams,minimum||0),x=t=>62+450*t/data.duration_minutes,y=v=>185-145*v/maximum;
  shape('text',{x:62,y:18},'Combustível disponível (kg)');
  for(let i=0;i<=4;i++){const fuel=maximum*i/4,minute=data.duration_minutes*i/4;shape('line',{x1:62,y1:y(fuel),x2:512,y2:y(fuel),stroke:'#d5dfe8'});shape('text',{x:55,y:y(fuel)+4,'text-anchor':'end'},new Intl.NumberFormat('pt-BR',{maximumFractionDigits:1}).format(fuel/1000));shape('text',{x:x(minute),y:205,'text-anchor':'middle'},new Intl.NumberFormat('pt-BR',{maximumFractionDigits:1}).format(minute));}
  if(minimum!==null&&minimum!==undefined)shape('line',{x1:62,y1:y(minimum),x2:512,y2:y(minimum),stroke:'#a34824','stroke-width':2,'stroke-dasharray':'7 5','aria-label':'Nível mínimo definido pelo operador'});
  shape('text',{x:287,y:226,'text-anchor':'middle'},'Tempo futuro (min)');shape('polyline',{points:data.curve.map(p=>`${x(p.minute_offset)},${y(p.available_grams)}`).join(' '),fill:'none',stroke:'#176a8a','stroke-width':3});return svg;
}
