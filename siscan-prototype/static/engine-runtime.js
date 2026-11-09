function renderEngineRuntime(parent,instructor,onContinued) {
  const panel=el("section",{class:"compiled-component runtime-panel","aria-label":"Execução sintética"});
  parent.append(panel);let pending=null,pendingContinuation=null,selectedRun=null;
  const format=value=>new Intl.NumberFormat('pt-BR',{maximumFractionDigits:3}).format(value);
  const load=async(clearPending=false)=>{
    panel.replaceChildren(el("p",{role:"status",text:"Consultando estado atual do ensaio…"}));
    try{
      const data=await api('/api/engine-runtime'+(selectedRun?'?run_id='+encodeURIComponent(selectedRun):''));if(clearPending){pending=null;pendingContinuation=null;}
      panel.replaceChildren(el("h3",{text:"Execução sintética — consumo constante"}),el("p",{class:"source-caveat",text:"Ensaio manual das unidades capturadas. Usa apenas parâmetros sintéticos; não representa voo, curvas Command ou consumo operacional. A alocação controla visibilidade, não a participação neste teste."}));
      if(!data.initialized){
        panel.append(el("p",{class:"muted",text:instructor?"O ensaio ainda não foi inicializado. Os snapshots existentes serão preservados.":"Nenhuma execução de teste disponível para as unidades do seu partido."}));
        if(instructor){const start=el("button",{class:"btn btn-secondary",type:"button",text:"Inicializar execução sintética"});start.addEventListener('click',async()=>{start.disabled=true;try{await api('/api/engine-runtime/start',{});await load();}catch(e){panel.append(el('p',{role:'alert',class:'notice error',text:e.message}));start.disabled=false;}});panel.append(start);}
        return;
      }
      panel.append(el("p",{class:"compiled-coverage runtime-clock",text:`Tempo do ensaio: ${data.elapsed_minutes} min · revisão ${data.revision}`}));
      panel.append(el('p',{class:'muted',text:`Cenário v${data.scenario_version} · ${data.is_current?'Execução atual':'Histórico preservado — somente leitura'}`}));
      if(data.manifest?.previous_run_id)panel.append(el('p',{class:'muted',text:'Tempo e consumo acumulados incluem a execução anterior. Os movimentos abaixo pertencem à versão selecionada.'}));
      const table=el("table",{class:"technical-matrix"});table.append(el("thead",{},[el("tr",{},['Unidade','Inicial (kg)','Saldo atual (kg)','Consumido (kg)'].map(text=>el('th',{scope:'col',text})))]));
      const body=el('tbody');for(const state of data.states)body.append(el('tr',{},[el('td',{text:state.code}),...[state.fuel_initial_kg,state.fuel_remaining_kg,state.fuel_consumed_kg].map(v=>el('td',{text:format(v)}))]));table.append(body);panel.append(el('div',{class:'technical-table-scroll',tabindex:'0'},[table]));
      if(instructor&&data.is_current){
        renderEngineProfile(panel,data);
        const form=el('form',{class:'runtime-form'}),input=el('input',{id:'runtime-minutes',type:'number',min:'1',max:'1440',step:'1',value:'30',required:'required'}),button=el('button',{class:'btn',type:'submit',text:pending?'Repetir comando pendente':'Avançar ensaio'}),status=el('p',{role:'status'});
        form.append(el('label',{class:'label',for:'runtime-minutes',text:'Intervalo de teste (minutos)'}),input,el('div',{class:'actions'},[button]),status);
        if(!data.advance_allowed){input.disabled=true;button.disabled=true;status.textContent='Cenário ou versão do motor mudou. O histórico foi preservado; novo avanço está bloqueado.';}
        if(pending){input.value=String(pending.minutes);input.disabled=true;}
        form.addEventListener('submit',async e=>{
          e.preventDefault();button.disabled=true;
          if(!pending)pending={command_id:crypto.randomUUID(),run_id:data.run_id,minutes:Number(input.value),expected_revision:data.revision};
          try{await api('/api/engine-runtime/advance',pending);pending=null;await load();}
          catch(error){status.textContent=error.message+' Para consultar o estado persistido antes de outro comando, use Atualizar estado.';input.disabled=true;button.textContent='Repetir comando pendente';button.disabled=false;}
        });panel.append(form);
        const continuation=el('details',{class:'equipment-group'},[el('summary',{text:'Continuar em nova versão'})]);
        continuation.append(el('p',{text:'Preserva tempo e combustível atuais e cria novos snapshots. A execução anterior fica disponível para consulta. Não reabastece as unidades.'}));
        const reason=el('textarea',{id:'runtime-continuation-reason',maxlength:'1000',required:'required',rows:'3'}),next=el('button',{class:'btn btn-secondary',type:'submit',text:pendingContinuation?'Repetir continuação pendente':'Criar continuação'}),notice=el('p',{role:'status'}),formNext=el('form',{class:'runtime-form'});
        if(pendingContinuation){reason.value=pendingContinuation.reason;reason.disabled=true;}
        formNext.append(el('label',{class:'label',for:'runtime-continuation-reason',text:'Motivo da nova versão'}),reason,next,notice);
        formNext.addEventListener('submit',async event=>{event.preventDefault();next.disabled=true;
          if(!pendingContinuation)pendingContinuation={command_id:crypto.randomUUID(),previous_run_id:data.run_id,expected_revision:data.revision,reason:reason.value};
          try{await api('/api/engine-runtime/continue',pendingContinuation);pendingContinuation=null;pending=null;selectedRun=null;if(onContinued)await onContinued();else await load();}
          catch(error){notice.textContent=error.message;reason.disabled=true;next.textContent='Repetir continuação pendente';next.disabled=false;}
        });continuation.append(formNext);panel.append(continuation);
      }
      const history=el('details',{class:'equipment-group'},[el('summary',{text:`Movimentos recentes de combustível · ${data.ledger.length}`})]);
      for(const row of data.ledger)history.append(el('p',{class:'runtime-ledger',text:`Revisão ${row.revision} · ${row.duration_minutes} min · ${format(row.before_grams/1000)} − ${format(row.consumed_grams/1000)} = ${format(row.after_grams/1000)} kg · unidade ${row.unit_id} · comando ${row.command_id}`}));
      panel.append(history,el('small',{class:'muted runtime-manifest',text:`Execução ${data.run_id} · manifesto ${data.manifest_sha256}`}));
      if(instructor){
        const archive=await api('/api/engine-runtime/history'),selector=el('select',{id:'runtime-history'});
        for(const run of archive.runs){const option=el('option',{value:run.run_id,text:`${run.run_id===archive.current_run_id?'Atual':'Histórico'} · cenário v${run.scenario_version} · ${run.elapsed_minutes} min · revisão ${run.revision} · ${run.run_id.slice(0,8)}`});option.selected=run.run_id===data.run_id;selector.append(option);}
        selector.addEventListener('change',()=>{selectedRun=selector.value;pending=null;pendingContinuation=null;load();});
        panel.append(el('label',{class:'label',for:'runtime-history',text:'Consultar execuções preservadas'}),selector);
        const selected=archive.runs.find(run=>run.run_id===data.run_id);if(selected?.reason)panel.append(el('p',{text:'Motivo: '+selected.reason}));
      }
    }catch(error){panel.replaceChildren(el('p',{role:'alert',class:'notice error',text:error.message}));}
    finally{panel.append(el('button',{class:'btn btn-secondary',type:'button',text:'Atualizar estado',onclick:()=>load(true)}));}
  };
  load();
}
