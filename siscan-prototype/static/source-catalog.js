function renderTechnicalCatalog(parent) {
  const categories = { DataAircraft: "Aeronaves", DataShip: "Navios", DataSubmarine: "Submarinos", DataGroundUnit: "Meios terrestres", DataFacility: "Instalações", DataSatellite: "Satélites" };
  const labels = { ID:"ID na fonte",Category:"Categoria",Type:"Tipo",OperatorCountry:"País do operador",OperatorService:"Força / serviço",YearCommissioned:"Entrada em serviço na fonte",YearDecommissioned:"Saída de serviço na fonte",Length:"Comprimento",Span:"Envergadura",Beam:"Boca",Draft:"Calado",Height:"Altura",Width:"Largura",Area:"Área",MastHeight:"Altura do mastro",Mass:"Massa",WeightEmpty:"Peso vazio",WeightMax:"Peso máximo",Crew:"Tripulação",MaxDepth:"Profundidade máxima",DisplacementEmpty:"Deslocamento vazio",DisplacementStandard:"Deslocamento padrão",DisplacementFull:"Deslocamento pleno" };
  const groupLabels = { Sensors:"Sensores",Mounts:"Suportes e armamentos",Magazines:"Paióis",Loadouts:"Configurações de carga",Fuel:"Combustível",Propulsion:"Propulsão",Comms:"Comunicações",Signatures:"Assinaturas",Codes:"Características codificadas",Weapons:"Registros de armamento",MagazineWeapons:"Armas do paiol",Warheads:"Ogivas",Directors:"Diretores",Capabilities:"Capacidades codificadas",Performance:"Desempenho",AircraftFacilities:"Instalações aeronáuticas",DockingFacilities:"Instalações de atracação" };
  const frame=el("section",{class:"technical-workspace","aria-label":"Catálogo técnico"});
  const heading=el("div",{class:"catalog-heading"},[el("div",{},[el("p",{class:"eyebrow",text:"SISCAN / BIBLIOTECA DE MEIOS"}),el("h1",{text:"Catálogo técnico"}),el("p",{class:"muted",text:"Explore plataformas, equipamentos e configurações da fonte Command."})]),el("span",{class:"source-status",text:"DB3K · dados de origem"})]);
  const rail=el("aside",{class:"catalog-rail","aria-label":"Seleção de meios"});
  const categoryBar=el("div",{class:"catalog-categories","aria-label":"Categorias"});
  const form=el("form",{class:"catalog-search"});
  const componentTypes={DataSensor:"Sensores",DataFuel:"Combustível",DataPropulsion:"Propulsão",DataMount:"Suportes",DataMagazine:"Paióis",DataLoadout:"Configurações de carga",DataWeaponRecord:"Registros de arma",DataWeapon:"Armas",DataWarhead:"Ogivas",DataComm:"Comunicações",DataAircraftFacility:"Instalações aeronáuticas",DataDockingFacility:"Atracação",DataContainer:"Contêineres"};
  const componentFilter=el("select",{id:"technical-component-type"});
  componentFilter.append(el("option",{value:"",text:"Selecionar biblioteca de componentes"}));
  for(const [value,text] of Object.entries(componentTypes))componentFilter.append(el("option",{value,text}));
  componentFilter.addEventListener("change",()=>{if(componentFilter.value){table=componentFilter.value;term="";search.value="";page=1;loadList();}});
  const search=el("input",{id:"technical-search",type:"search",maxlength:"120",placeholder:"Nome ou ID externo"});
  form.append(el("label",{for:"technical-search",class:"label",text:"Localizar meio"}),search,el("button",{type:"submit",class:"btn",text:"Pesquisar"}));
  const status=el("p",{class:"catalog-result-count",role:"status"});
  const results=el("div",{class:"platform-results","aria-label":"Meios encontrados"});
  const prev=el("button",{type:"button",class:"btn btn-secondary",text:"Anterior"});
  const next=el("button",{type:"button",class:"btn btn-secondary",text:"Próxima"});
  const pagination=el("div",{class:"catalog-pagination"},[prev,next]);
  rail.append(categoryBar,el("div",{class:"component-library"},[el("label",{class:"label",for:"technical-component-type",text:"Bibliotecas técnicas"}),componentFilter]),form,status,results,pagination);
  const viewer=el("article",{class:"platform-viewer","aria-label":"Ficha do meio","aria-busy":"false"});
  const engineButton=el("button",{type:"button",class:"btn btn-secondary","aria-expanded":"false","aria-controls":"engine-readiness-panel",text:"Preparação do motor"});
  const enginePanel=el("section",{id:"engine-readiness-panel",class:"engine-readiness-panel dossier-section",hidden:true,"aria-label":"Diagnóstico de entrada do motor","aria-live":"polite"});
  let engineLoaded=false;
  const checkEngine=async()=>{
    engineButton.disabled=true;enginePanel.replaceChildren(el("p",{role:"status",text:"Conferindo contrato e versões das bases…"}));
    try{
      const report=await api('/api/engine-readiness');
      const validation=report.validation,catalog=report.catalog;
      enginePanel.replaceChildren(el("h2",{text:"Entrada do motor"}),el("p",{class:validation.accepted?"compiled-coverage":"notice error",text:validation.accepted?"Contrato sintético: aceito para teste controlado.":"Contrato sintético: recusado. Confira as pendências abaixo."}),el("p",{class:"muted",text:report.qualification}));
      const fields=el("dl",{class:"technical-grid"}),labels={fuel_capacity:"Capacidade de combustível",fuel_initial:"Combustível inicial",consumption_rate:"Taxa de consumo",duration:"Duração de referência"};
      for(const [name,item] of Object.entries(report.synthetic_input?.measurements||{}))fields.append(el("div",{class:"technical-field"},[el("dt",{text:labels[name]||name}),el("dd",{text:`${item.value} ${item.unit}`} )]));
      enginePanel.append(el("h3",{text:"Conjunto sintético de referência"}),fields);
      for(const error of validation.errors)enginePanel.append(el("p",{class:"notice error",text:`${error.field}: ${error.message}`}));
      enginePanel.append(el("h3",{text:"Compatibilidade das bases Command"}),el("p",{class:catalog.structurally_compatible?"compiled-coverage":"source-caveat",text:catalog.structurally_compatible?"Arquivos e versões conferidos. A validação física dos dados permanece pendente.":"Há arquivos ausentes ou versões incompatíveis. Isso não impede o teste sintético independente."}));
      const checks=el("ul");for(const check of catalog.checks)checks.append(el("li",{text:`${check.ok?"Conferido":"Requer revisão"}: ${check.message}`}));enginePanel.append(checks,el("p",{class:"source-caveat",text:catalog.qualification}));
      const manifest=el("details",{class:"equipment-group engine-manifest"},[el("summary",{text:"Manifesto e rastreabilidade"})]);
      for(const [key,value] of Object.entries(validation.manifest))manifest.append(el("p",{},[el("strong",{text:key+": "}),el("span",{text:String(value)})]));
      for(const artifact of Object.values(catalog.artifacts))manifest.append(el("p",{text:`${artifact.file_name}: ${artifact.sha256}`}));
      enginePanel.append(manifest,el("button",{type:"button",class:"btn btn-secondary",text:"Atualizar verificação",onclick:checkEngine}));engineLoaded=true;
    }catch(error){enginePanel.replaceChildren(el("p",{class:"notice error",role:"alert",text:error.message}));engineLoaded=false;}
    finally{engineButton.disabled=false;}
  };
  engineButton.addEventListener("click",()=>{enginePanel.hidden=!enginePanel.hidden;engineButton.setAttribute("aria-expanded",String(!enginePanel.hidden));if(!enginePanel.hidden&&!engineLoaded)checkEngine();});
  frame.append(heading,el("div",{class:"actions engine-controls"},[engineButton]),enginePanel,el("div",{class:"catalog-layout"},[rail,viewer]));parent.append(frame);
  let table="DataAircraft",page=1,term="",listSequence=0,detailSequence=0;
  const categoryButtons={};
  for(const [key,title] of Object.entries(categories)) {
    const button=el("button",{type:"button",class:"category-choice",text:title,"aria-pressed":key===table?"true":"false"});
    button.addEventListener("click",()=>{table=key;componentFilter.value="";term="";search.value="";page=1;loadList();});
    categoryButtons[key]=button;categoryBar.append(button);
  }
  const valueText=value=>value===null?"NULL na fonte":typeof value==="object"?JSON.stringify(value):String(value);
  const fieldList=(fields,domains={},measurements={})=>{
    const list=el("dl",{class:"technical-grid"});
    for(const [key,value] of fields) {
      const description=domains[key]?.description;
      list.append(el("div",{class:"technical-field",title:measurements[key]?.qualification||""},[el("dt",{text:measurementLabel(labels[key]||key,measurements[key])}),el("dd",{text:`${valueText(value)}${description?" · "+description:""}`})]));
    }return list;
  };
  async function openRecord(recordTable,id,selectedButton) {
    const sequence=++detailSequence;
    for(const button of results.querySelectorAll("button"))button.setAttribute("aria-pressed",String(button===selectedButton));
    viewer.setAttribute("aria-busy","true");viewer.replaceChildren(el("p",{class:"viewer-empty",text:"Abrindo ficha técnica…"}));
    try {
      const data=await api(`/api/source-platform?${new URLSearchParams({table:recordTable,id:String(id)})}`);
      if(sequence!==detailSequence)return;
      const fields=data.fields,name=data.display_name||fields.Name||`${recordTable} #${id}`;
      const subtitle=[data.domains.OperatorCountry?.description,fields.YearCommissioned?String(fields.YearCommissioned):null,`ID ${id}`].filter(Boolean).join(" · ");
      viewer.replaceChildren();
      viewer.append(el("header",{class:"platform-header"},[el("p",{class:"eyebrow",text:categories[recordTable]||"COMPONENTE DA FONTE"}),el("h2",{text:name}),el("p",{class:"platform-subtitle",text:subtitle}),el("span",{class:"source-status",text:"Validação técnica pendente"})]));
      if(data.photo_url) {
        const image=el("img",{src:data.photo_url,alt:`Imagem local associada a ${name}`,class:"platform-photo"});
        const figure=el("figure",{class:"platform-figure"},[image,el("figcaption",{text:"Imagem ilustrativa da instalação local do Command, associada ao ID da fonte."})]);
        image.addEventListener("error",()=>figure.replaceChildren(el("p",{class:"photo-empty",text:"Imagem local não disponível."})),{once:true});viewer.append(figure);
      } else viewer.append(el("div",{class:"photo-empty",text:"Sem imagem local para este registro"}));
      const body=el("div",{class:"platform-body"});
      body.append(el("p",{class:"source-caveat",text:"Valores originais. As unidades identificam evidências amostrais ou referências documentais; as pendentes são indicadas em cada campo. Consulte Unidades e evidências desta ficha para os limites."}));
      const primary=Object.entries(fields).filter(([key])=>key in labels);
      body.append(el("section",{class:"dossier-section"},[el("h3",{text:"Dados gerais"}),fieldList(primary,data.domains,data.measurements)]));
      const compiled=el("div",{class:"compiled-bundle-host"});
      compiled.append(el("p",{role:"status",class:"muted",text:"Reunindo sensores, combustível e regimes de consumo…"}));
      body.append(compiled);
      const loadCompiled=async()=>{
        try {
          const bundle=await api(`/api/source-technical?${new URLSearchParams({table:recordTable,id:String(id)})}`);
          if(sequence===detailSequence)renderTechnicalBundle(compiled,bundle);
        }catch(error){
          if(sequence!==detailSequence)return;
          compiled.replaceChildren(el("p",{class:"notice error",role:"alert",text:error.message}),el("button",{type:"button",class:"btn btn-secondary",text:"Tentar reunir dados novamente",onclick:loadCompiled}));
        }
      };
      loadCompiled();
      for(const link of data.direct_links) {
        if(link.id!==null)body.append(el("button",{type:"button",class:"component-link",text:`Abrir ${link.name||link.table} · ID ${link.id}`,onclick:()=>openRecord(link.table,link.id)}));
      }
      const groups=el("section",{class:"dossier-section"},[el("h3",{text:"Equipamentos e associações"})]);
      let groupCount=0;
      for(const [key,items] of Object.entries(data.groups)) {
        const suffix=key.startsWith(recordTable)?key.slice(recordTable.length):key;
        const details=el("details",{class:"equipment-group"});
        details.append(el("summary",{text:`${groupLabels[suffix]||suffix} · ${items.length}`}));
        for(const item of items) {
          const row=el("div",{class:"component-row"});
          const title=item.target_name||`${item.target_table||key}${item.target_id!==null?" #"+item.target_id:""}`;
          if(item.target_id!==null && item.target_table?.startsWith("Data"))row.append(el("button",{type:"button",class:"component-link",text:title,onclick:()=>openRecord(item.target_table,item.target_id)}));
          else row.append(el("strong",{text:title}));
          row.append(el("small",{text:item.component_basis==="declared_fk"?"Relação declarada na fonte":item.status==="matched"?"Ligação estrutural com registro correspondente; sem FK declarada":item.status?`Ligação ${item.status} · requer avaliação`:"Características do registro de associação"}));
          const parameters=el("details",{class:"component-parameters"});parameters.append(el("summary",{text:"Parâmetros originais"}),fieldList(Object.entries(item.parameters),{},item.measurements));row.append(parameters);details.append(row);
        }groups.append(details);groupCount+=items.length;
      }
      if(!groupCount)groups.append(el("p",{class:"muted",text:"Nenhuma associação de componentes encontrada nesta fonte."}));
      if(data.truncated)groups.append(el("p",{class:"source-caveat",text:"Exibidos os primeiros 1.000 registros de associação desta ficha."}));
      body.append(groups);
      const remaining=Object.entries(fields).filter(([key])=>!(key in labels)&&key!=="Name"&&key!=="Comments");
      const extra=el("details",{class:"equipment-group"});extra.append(el("summary",{text:`Demais atributos da fonte · ${remaining.length}`}),fieldList(remaining,data.domains,data.measurements));body.append(extra);
      if(fields.Comments)body.append(el("details",{class:"equipment-group"},[el("summary",{text:"Observações da fonte"}),el("p",{class:"review-note-text",text:fields.Comments})]));
      const provenance=el("details",{class:"equipment-group provenance"});provenance.append(el("summary",{text:"Origem e rastreabilidade"}),el("p",{class:"source-hash",text:`${data.source.file_name} · ${recordTable}/${id} · SHA-256 ${data.source.sha256}`}),el("p",{text:data.reference_id?`Referência SISCAN: ${data.reference_id}`:"Registro compilado da fonte; não promovido a referência operacional."}));body.append(provenance);viewer.append(body);
    }catch(error){if(sequence===detailSequence)viewer.replaceChildren(el("p",{class:"notice error",role:"alert",text:error.message}));}
    finally{if(sequence===detailSequence)viewer.setAttribute("aria-busy","false");}
  }
  async function loadList() {
    const sequence=++listSequence;++detailSequence;
    prev.disabled=true;next.disabled=true;results.replaceChildren();status.textContent="Consultando catálogo…";
    for(const [key,button] of Object.entries(categoryButtons))button.setAttribute("aria-pressed",String(key===table));
    try {
      const data=await api(`/api/source-platforms?${new URLSearchParams({table,q:term,page:String(page)})}`);
      if(sequence!==listSequence)return;
      page=data.page;status.textContent=`${data.total} registros · ${data.page} / ${data.pages}`;
      for(const [key,button] of Object.entries(categoryButtons))button.textContent=`${categories[key]}  ${data.categories[key]??0}`;
      for(const item of data.items) {
        const itemTable=data.table;
        const button=el("button",{type:"button",class:"platform-choice","aria-pressed":"false"},[el("strong",{text:item.name}),el("small",{text:`ID ${item.id}${item.year?" · "+item.year:""}${item.hypothetical===1?" · Hipotético na fonte":""}`})]);
        button.addEventListener("click",()=>openRecord(itemTable,item.id,button));results.append(button);
      }
      prev.disabled=page<=1;next.disabled=page>=data.pages;
      if(data.items.length)openRecord(data.table,data.items[0].id,results.firstElementChild);
      else viewer.replaceChildren(el("p",{class:"viewer-empty",text:"Nenhum meio corresponde à pesquisa."}));
    }catch(error){if(sequence===listSequence){status.textContent="Consulta indisponível";viewer.replaceChildren(el("p",{class:"notice error",role:"alert",text:error.message}));}}
  }
  form.addEventListener("submit",event=>{event.preventDefault();term=search.value.trim();page=1;loadList();});
  prev.addEventListener("click",()=>{page--;loadList();});next.addEventListener("click",()=>{page++;loadList();});
  loadList();
}
