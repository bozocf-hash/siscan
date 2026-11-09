function measurementLabel(label, info) {
  if(!info)return label;
  if(!info.display_unit)return `${label} (unidade a confirmar)`;
  const qualifier=info.status==="observed_sample"||info.status==="observed_label"?"amostra":info.status==="field_meaning"?"contagem":"referência";
  return `${label} (${info.display_unit} · ${qualifier})`;
}

function renderTechnicalBundle(parent, bundle) {
  const nodes=new Map(bundle.nodes.map(node=>[node.key,node]));
  const root=nodes.get(bundle.root),outgoing=new Map(),owned=new Map();
  for(const link of bundle.links) {
    if(!outgoing.has(link.source))outgoing.set(link.source,[]);
    outgoing.get(link.source).push(link);
    if(link.field==="ID" && link.target) {
      if(!owned.has(link.target))owned.set(link.target,new Set());
      owned.get(link.target).add(link.source);
    }
  }
  const labels={ID:"ID na fonte",Type:"Tipo",Capacity:"Capacidade",RangeMin:"Alcance mínimo",RangeMax:"Alcance máximo",AltitudeMin:"Altitude mínima",AltitudeMax:"Altitude máxima",AltitudeMin_ASL:"Altitude mínima ASL",AltitudeMax_ASL:"Altitude máxima ASL",ScanInterval:"Intervalo de varredura",Generation:"Geração",Role:"Função",Frequency:"Frequência / banda",ComponentID:"ID do componente",ComponentNumber:"Número do componente",AltitudeBand:"Faixa de altitude",Throttle:"Regime",Speed:"Velocidade",Consumption:"Consumo",NumberOfEngines:"Número de motores",SFCMilitary:"SFC military",SFCAfterburner:"SFC afterburner",ThrustPerEngineMilitary:"Empuxo por motor military",ThrustPerEngineAfterburner:"Empuxo por motor afterburner"};
  const throttle=bundle.reference_annotations.throttle_codes;
  const format=value=>value===null?"NULL":typeof value==="object"?JSON.stringify(value):String(value);
  const valueText=(node,field)=>{
    const raw=format(node.fields[field]);
    const link=(outgoing.get(node.key)||[]).find(l=>l.field===field && l.target);
    const target=link?nodes.get(link.target):null;
    const description=target?.fields.Description||target?.fields.Name;
    return description?`${raw} · ${description}`:raw;
  };
  const children=node=>[...(owned.get(node.key)||[])].map(key=>nodes.get(key));
  const directKeys=new Set();
  for(const child of children(root))for(const link of outgoing.get(child.key)||[])if(link.field==="ComponentID" && link.target)directKeys.add(link.target);
  const fieldsView=node=>{
    const list=el("dl",{class:"technical-grid"});
    for(const field of Object.keys(node.fields))list.append(el("div",{class:"technical-field",title:node.measurements?.[field]?.qualification||""},[el("dt",{text:measurementLabel(labels[field]||field,node.measurements?.[field])}),el("dd",{class:"raw-field-value",text:valueText(node,field)})]));
    return list;
  };
  const lazy=(title,build,attrs={})=>{
    const details=el("details",{class:"equipment-group",...attrs},[el("summary",{text:title})]);
    let rendered=false;
    details.addEventListener("toggle",()=>{if(details.open&&!rendered){rendered=true;details.append(build());}});
    return details;
  };
  const matrix=rows=>{
    const wrapper=el("div",{class:"technical-table-scroll",tabindex:"0"});
    const table=el("table",{class:"technical-matrix"});
    const performance=rows.every(row=>row.table==="DataPropulsionPerformance");
    const available=[...new Set(rows.flatMap(row=>Object.keys(row.fields)))];
    const priority=["Throttle","Speed","Consumption","AltitudeBand","AltitudeMin","AltitudeMax","ID"];
    const columns=performance?[...priority.filter(field=>available.includes(field)),...available.filter(field=>!priority.includes(field))]:available;
    const headings=performance?{AltitudeBand:"Faixa",AltitudeMin:"Alt. mín.",AltitudeMax:"Alt. máx."}:{};
    const contracts=Object.fromEntries(columns.map(field=>{
      const variants=[...new Set(rows.map(row=>JSON.stringify(row.measurements?.[field]||null)))];
      return [field,variants.length===1?JSON.parse(variants[0]):null];
    }));
    table.append(el("thead",{},[el("tr",{},columns.map(field=>el("th",{scope:"col",text:measurementLabel(headings[field]||labels[field]||field,contracts[field])})))]));
    const body=el("tbody");
    for(const row of rows)body.append(el("tr",{},columns.map(field=>{
      let text=field in row.fields?(performance?format(row.fields[field]):valueText(row,field)):"Campo ausente";
      if(row.table==="DataPropulsionPerformance"&&field==="Throttle"&&row.fields[field] in throttle)text+=` · ${throttle[row.fields[field]]}`;
      if(!contracts[field]&&row.measurements?.[field])text+=` · ${row.measurements[field].display_unit||"unidade a confirmar"} (${row.measurements[field].status})`;
      return el("td",{text,title:row.measurements?.[field]?.qualification||""});
    })));
    table.append(body);wrapper.append(table);return wrapper;
  };
  const section=el("section",{class:"dossier-section compiled-technical","aria-label":"Dados técnicos compilados"});
  section.append(el("h3",{text:"Dados técnicos compilados"}),el("p",{class:"compiled-coverage",role:"status",text:`${bundle.node_count} registros associados · ${bundle.field_count} campos preservados · cadeia reunida integralmente pelas relações mapeadas`}),el("p",{class:"muted",text:"Os dados do meio e dos componentes estão reunidos abaixo. Registros diretamente associados são separados dos existentes em equipamentos e armamentos. Valores e sinais são mantidos como na fonte."}));
  section.append(el("p",{class:"source-caveat",text:"Unidades junto aos campos: amostra = apresentação observada; referência = unidade documental proposta para o campo SQL. Unidade a confirmar = evidência insuficiente. Valores brutos preservados; referências ainda não liberam cálculos."}));
  const drawFamily=(table,title)=>{
    const all=bundle.nodes.filter(node=>node.table===table);
    const group=el("section",{class:"compiled-family"});
    group.append(el("h4",{text:title}));
    if(table==="DataFuel")group.append(el("p",{class:"muted",text:"Capacidade é estoque. O consumo por velocidade, regime e faixa está em Propulsão, regimes e consumo, logo abaixo. Não há média única: ela depende do tempo em cada condição. Bateria, combustível líquido e tempo de propulsão não são somáveis."}));
    if(!all.length){group.append(el("p",{class:"muted",text:"Nenhum registro desta família foi encontrado na cadeia mapeada desta fonte."}));section.append(group);return;}
    const appendNode=(target,node,direct)=>{
      const card=el("article",{class:"compiled-component","data-source-key":node.key});
      card.append(el("header",{},[el("strong",{text:node.fields.Name||(table==="DataFuel"?`${valueText(node,"Type")} · ID ${node.id}`:`${table} · ID ${node.id}`)}),el("span",{class:"component-context",text:direct?"Associado diretamente ao registro selecionado":"Componente da cadeia de equipamentos / armamentos"})]));
      const highlights=table==="DataSensor"?["Type","Role","RangeMin","RangeMax","ScanInterval"]:table==="DataFuel"?["Type","Capacity"]:["Type","NumberOfEngines","SFCMilitary","SFCAfterburner"];
      const summary=el("dl",{class:"technical-grid"});
      for(const field of highlights)if(field in node.fields)summary.append(el("div",{class:"technical-field",title:node.measurements?.[field]?.qualification||""},[el("dt",{text:measurementLabel(labels[field]||field,node.measurements?.[field])}),el("dd",{text:valueText(node,field)})]));
      card.append(summary,lazy(`Todos os campos · ${Object.keys(node.fields).length}`,()=>fieldsView(node)));
      const groups=new Map();
      for(const child of children(node)){if(!groups.has(child.table))groups.set(child.table,[]);groups.get(child.table).push(child);}
      for(const [name,rows] of groups) {
        if(name==="DataPropulsionPerformance") {
          card.append(el("h5",{text:`Regimes de desempenho e consumo · ${rows.length} registros`}),matrix(rows),el("p",{class:"table-footnote",text:"Referências: kn = milha náutica por hora; m = metro; kg/min = quilograma por minuto. Rótulos de referência não comprovam a escala SQL. Não multiplicar pelo número de motores nem aplicar modificadores de carga antes de validar a base do consumo."}));
        } else {
          const suffix=name.replace(table,"");
          const titles={FrequencySearchAndTrack:"Frequências de busca e acompanhamento",FrequencyIlluminate:"Frequências de iluminação",Capabilities:"Capacidades",Codes:"Características codificadas",SensorGroups:"Sensores integrantes do grupo"};
          card.append(lazy(`${titles[suffix]||suffix||name} · ${rows.length}`,()=>matrix(rows)));
        }
      }
      if(table==="DataPropulsion"&&!groups.has("DataPropulsionPerformance"))card.append(el("p",{class:"table-footnote",text:"A fonte não contém linhas de regime/desempenho para este cadastro de propulsão. Nenhum consumo foi preenchido por suposição."}));
      const installations=children(root).filter(child=>(outgoing.get(child.key)||[]).some(link=>link.field==="ComponentID"&&link.target===node.key));
      if(installations.length)card.append(lazy(`Registros de instalação no meio · ${installations.length}`,()=>matrix(installations)));
      card.append(el("small",{class:"muted",text:`Origem: ${node.table} / ID ${node.id} / linha ${node.rowid}`}));target.append(card);
    };
    const direct=all.filter(node=>directKeys.has(node.key)||node.key===root.key);
    for(const node of direct)appendNode(group,node,true);
    const indirect=all.filter(node=>!direct.includes(node));
    if(indirect.length)group.append(lazy(`Componentes associados por outras cadeias · ${indirect.length}`,()=>{
      const content=el("div");for(const node of indirect)appendNode(content,node,false);return content;
    }));
    section.append(group);
  };
  drawFamily("DataSensor","Sensores, frequências e capacidades");
  drawFamily("DataFuel","Combustível e armazenamento");
  drawFamily("DataPropulsion","Propulsão, regimes e consumo");
  section.append(lazy("Unidades e evidências desta ficha",()=>{
    const content=el("div"),seen=new Set();
    for(const node of bundle.nodes)for(const [field,info] of Object.entries(node.measurements||{})) {
      const key=JSON.stringify([node.table,field,info]);if(seen.has(key))continue;seen.add(key);
      const item=el("p",{class:"unit-evidence"},[el("strong",{text:measurementLabel(`${node.table}.${field}`,info)}),el("span",{text:` — ${info.qualification} `})]);
      if(info.evidence?.startsWith("https://"))item.append(el("a",{href:info.evidence,target:"_blank",rel:"noopener noreferrer",text:"Consultar fonte"}));
      else if(info.evidence)item.append(el("small",{text:`Registro: ${info.evidence}`}));
      content.append(item);
    }return content;
  }));
  section.append(lazy(`Todos os registros compilados · ${bundle.node_count}`,()=>{
    const content=el("div");
    for(const table of Object.keys(bundle.table_counts).sort()) {
      const rows=bundle.nodes.filter(node=>node.table===table);
      content.append(lazy(`${table} · ${rows.length}`,()=>matrix(rows)));
    }return content;
  }));
  const missing=bundle.links.filter(link=>link.status!=="matched");
  if(missing.length)section.append(lazy(`Vínculos sem correspondência · ${missing.length}`,()=>el("div",{},missing.map(link=>el("p",{text:`${link.source}.${link.field} → ${link.target_table}.${link.target_field}: ${format(link.raw_key)} · ${link.status}`})))));
  const download=el("button",{type:"button",class:"btn btn-secondary",text:"Baixar ficha compilada (JSON)"});
  download.addEventListener("click",()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(bundle,null,2)],{type:"application/json"}));
    const link=el("a",{href:url,download:`${root.table}_${root.id}_dados_compilados.json`});link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  section.append(el("div",{class:"actions"},[download]));parent.replaceChildren(section);
}
