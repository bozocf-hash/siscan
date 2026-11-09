"""Versioned display evidence; never silently approve SQL quantities for a motor."""
VERSION='db3k-498-units-01'
MANUAL='https://ftp.matrixgames.com/pub/CommandModernOperations/CMO%20manual%20EBOOK.pdf'
API='https://commandlua.github.io/assets/DataTypes.html'
SAMPLE='docs/recovery/59_ROTEIRO_COMPARACAO_VISUAL_DB3K.md'
TEMPLATES='docs/recovery/58_FONTES_LOCAIS_CMO_E_TEMPLATES.md'
UNKNOWN='Unidade SQL não confirmada; valor original, sem conversão.'


def evidence(symbol=None, status='unconfirmed', source=None, note=UNKNOWN):
    return {'unit':None,'candidate_unit':symbol,'display_unit':symbol,
            'status':status,'evidence':source,'qualification':note,
            'calculation_ready':False,'contract_version':VERSION}


def describe_fields(table, fields, domain_fields=(), propulsion_type=None):
    """Attach field-specific evidence, including explicit unknowns for numeric data."""
    result={}
    dimensions={
        'DataAircraft':{'Length','Span','Height'},
        'DataShip':{'Length','Beam','Draft','Height'},
        'DataSubmarine':{'Length','Beam','Draft','Height','MaxDepth'},
        'DataGroundUnit':{'Length','Width','MastHeight'},
        'DataSatellite':{'Length','Span','Height'},
    }
    code_fields={'ID','ComponentID','ComponentNumber','CodeID','Type','Category','Role',
                 'Generation','AltitudeBand','Throttle','MasqueradeAs','OperatorCountry',
                 'OperatorService','Hypothetical','Deprecated','IsOptional',
                 'YearCommissioned','YearDecommissioned'} | set(domain_fields)
    for field,value in fields.items():
        if field in {'Name','Comments','Description','Visibility'}:
            continue
        if not isinstance(value,(int,float)) and value is not None:
            continue
        if field in code_fields or table.startswith('Enum'):
            continue
        info=evidence()
        if field in dimensions.get(table,set()):
            sample=table!='DataSatellite' and not (table=='DataGroundUnit' and field=='MastHeight')
            info=evidence('m','observed_sample' if sample else 'template_reference',SAMPLE if sample else TEMPLATES,
                          'Unidade de apresentação observada em amostra 498a com valores SQL iguais no 498; não é aprovação operacional.' if sample else
                          'Rótulo do template local; conversão SQL não demonstrada. MastHeight terrestre divergiu na amostra.')
        elif table in {'DataAircraft','DataSatellite'} and field in {'WeightEmpty','WeightMax','WeightPayload'}:
            sample=table=='DataAircraft' and field!='WeightPayload'
            info=evidence('kg','observed_sample' if sample else 'template_reference',SAMPLE if sample else TEMPLATES,
                          'Apresentação em kg; correspondência amostral para WeightEmpty/WeightMax de Aircraft/3. Demais campos: template, sem validação SQL geral.')
        elif table in {'DataShip','DataSubmarine'} and field.startswith('Displacement'):
            info=evidence('tons','observed_label',SAMPLE,'Rótulo literal do visualizador: tons. Tipo de tonelada não confirmado; não converter para t/kg.')
        elif table=='DataFuel' and field=='Capacity':
            if fields.get('Type')==2001:
                info=evidence('kg','manual_reference',MANUAL+'#page=91',
                              'O painel de aeronave no manual usa kg. Correspondência à capacidade SQL ainda em validação; não converter para litros sem densidade.')
            elif fields.get('Type') in {4001,4002,4003,5003}:
                info=evidence(note='Energia, reagente ou tempo segundo o tipo; não tratar como kg ou litros sem comprovação.')
        elif table=='DataPropulsionPerformance':
            if field=='Speed':
                info=evidence('kn','manual_reference','https://command.matrixgames.com/manual/04-learning-by-example/',
                              'Nó: milha náutica por hora. Unidade de velocidade usada no manual; correspondência SQL ainda em validação.')
            elif field in {'AltitudeMin','AltitudeMax'}:
                info=evidence('m','api_reference',API+'#Altitude','Referência da API para altitude/profundidade; preservar sinal e faixa. Correspondência SQL ainda em validação.')
            elif field=='Consumption' and propulsion_type in {2001,2002,2003,2004,2005}:
                info=evidence('kg/min','manual_reference',MANUAL+'#page=91',
                              'Consumo de aeronave exibido em kg/min no manual. Escala SQL, total por conjunto e modificadores de carga ainda em validação.')
        elif table=='DataPropulsion' and field in {'SFCMilitary','SFCAfterburner'}:
            info=evidence(note='Consumo específico, distinto do fluxo Consumption. A unidade depende do tipo de motor; não usar como kg/min.')
        elif table=='DataPropulsion' and field=='NumberOfEngines':
            info=evidence('motores','field_meaning',note='Contagem no campo NumberOfEngines; zero e valores fracionários não foram reinterpretados.')
        elif table=='DataGroundUnit' and field=='Area':
            info=evidence(note='Area é rotulado m no template, mas a grandeza não foi confirmada. Não atribuir m² por inferência.')
        elif table=='DataSensor' and field=='RangeMax':
            info=evidence('NM','api_reference','https://commandlua.github.io/assets/Tables.html#Emissions',
                          'A API documenta sensor_maxrange em milhas náuticas (nm/NM). Correspondência à coluna RangeMax ainda em validação.')
        elif table=='DataSensor' and field in {'AltitudeMin','AltitudeMax','AltitudeMin_ASL','AltitudeMax_ASL'}:
            info=evidence('m','api_reference',API+'#Altitude','Referência da API para altitude/profundidade; unidade e referência vertical deste limite SQL ainda em validação.')
        elif field=='Crew':
            info=evidence('pessoas','field_meaning',SAMPLE,'Contagem de tripulação; composição por função não determinada.')
        result[field]=info
    return result


def annotate_bundle(nodes, links, root_key):
    by_key={n['key']:n for n in nodes}
    parents={l['source']:l['target'] for l in links if l['field']=='ID' and l.get('target')}
    domains={}
    for link in links:
        target=by_key.get(link.get('target'))
        if target and target['table'].startswith('Enum'):
            domains.setdefault(link['source'],set()).add(link['field'])
    direct={l['target'] for l in links if l['field']=='ComponentID' and l.get('target') and
            parents.get(l['source'])==root_key}
    performance={}
    for node in nodes:
        parent=by_key.get(parents.get(node['key']))
        kind=parent['fields'].get('Type') if parent and parent['table']=='DataPropulsion' else None
        node['measurements']=describe_fields(node['table'],node['fields'],domains.get(node['key'],()),kind)
        if node['table']=='DataPropulsionPerformance' and parent and parent['table']=='DataPropulsion':
            performance.setdefault(parent['key'],[]).append({
                'source_key':node['key'],'source_rowid':node['rowid'],
                'values':node['fields'],'measurements':node['measurements']})
    return [{'propulsion_key':node['key'],'propulsion_id':node['id'],
             'name':node['fields'].get('Name'),'direct':node['key']==root_key or node['key'] in direct,
             'points':performance.get(node['key'],[]),'calculation_ready':False,
             'average_consumption':None,
             'reason':'Média requer perfil temporal; unidades SQL, escala por conjunto e modificadores ainda precisam de validação.'}
            for node in nodes if node['table']=='DataPropulsion']
