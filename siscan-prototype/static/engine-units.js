function renderEngineUnits(parent,instructor) {
  const panel=el("details",{class:"card engine-units-panel","aria-label":"Unidades do motor"});
  panel.append(el("summary",{text:"Unidades de teste do motor"}),el("p",{class:"muted",text:"Identidade e dados iniciais preservados por snapshot. O painel de execução mantém tempo e combustível atuais separados dos dados congelados."}));
  const content=el("div");let loaded=false;
  const load=async()=>{
    content.replaceChildren(el("p",{role:"status",text:"Conferindo unidades e snapshots…"}));
    try {
      const data=await api('/api/engine-units');content.replaceChildren();
      if(!data.units.length)content.append(el("p",{class:"empty",text:instructor?"Nenhuma unidade de teste preparada neste exercício.":"Nenhuma unidade de teste disponibilizada ao seu partido."}));
      for(const unit of data.units) {
        const snapshot=unit.snapshot,card=el("article",{class:"compiled-component","data-unit-id":unit.unit_id});
        card.append(el("h3",{text:unit.name}),el("p",{class:"muted",text:`${unit.code} · ${unit.team} · ${unit.allocated?"Disponibilizada ao partido":"Aguardando disponibilização pelo instrutor"}`}));
        card.append(el("p",{class:"unit-identity",text:`ID da unidade: ${unit.unit_id}`}));
        if(snapshot.scenario_version!==data.current_scenario_version)card.append(el("p",{class:"source-caveat",text:`Snapshot do cenário ${snapshot.scenario_version}; cenário atual ${data.current_scenario_version}. Os dados congelados foram preservados.`}));
        const fields=el("dl",{class:"technical-grid"}),labels={fuel_capacity:"Capacidade inicial cadastrada",fuel_initial:"Combustível inicial",consumption_rate:"Taxa de referência",duration:"Duração de referência"};
        for(const [name,item] of Object.entries(snapshot.input_template.measurements))fields.append(el("div",{class:"technical-field"},[el("dt",{text:labels[name]||name}),el("dd",{text:`${item.value} ${item.unit}`} )]));
        card.append(fields);
        const detail=el("details",{class:"equipment-group engine-manifest"},[el("summary",{text:"Configuração e snapshot preservados"})]);
        for(const [label,value] of [["Modelo",snapshot.model_id],["Configuração",snapshot.configuration_id],["Versão da configuração",unit.configuration_version_id],["Snapshot",unit.snapshot_id],["Revisão",unit.revision],["Versão do cenário",snapshot.scenario_version],["Hash do snapshot",unit.snapshot_sha256],["Hash do conjunto",snapshot.input_manifest.dataset_sha256]])detail.append(el("p",{},[el("strong",{text:label+": "}),el("span",{text:String(value)})]));
        card.append(detail);content.append(card);
      }
      if(data.units.length)renderEngineRuntime(content,instructor);
      loaded=true;
    }catch(error){content.replaceChildren(el("p",{class:"notice error",role:"alert",text:error.message}));loaded=false;}
  };
  if(instructor) {
    const prepare=el("button",{class:"btn btn-secondary",type:"button",text:"Preparar unidades sintéticas dos partidos"});
    prepare.addEventListener("click",async()=>{
      prepare.disabled=true;
      try{await api('/api/engine-units/prepare',{});await loadDashboard();const next=document.querySelector('.engine-units-panel');if(next)next.open=true;}
      catch(error){content.replaceChildren(el("p",{class:"notice error",role:"alert",text:error.message}));}
      finally{prepare.disabled=false;}
    });
    panel.append(el("div",{class:"actions"},[prepare]),el("p",{class:"muted",text:"Uma unidade por partido. Repetir não duplica. Para disponibilizar aos alunos, use a alocação do partido em Exercício e revisão."}));
  }
  panel.append(content,el("button",{class:"btn btn-secondary",type:"button",text:"Atualizar unidades",onclick:load}));
  panel.addEventListener('toggle',()=>{if(panel.open&&!loaded)load();});parent.append(panel);
}
