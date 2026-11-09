"""Associate stored weapon masses with separate loadouts; comparisons are advisory."""
from collections import defaultdict
import math

VERSION='armament-payload-reference-01'
WEIGHT_SOURCE='https://github.com/PygmalionOfCyprus/cmo-db-requests/blob/main/.github/ISSUE_TEMPLATE/22_NEW-WEAPON.yml'


def number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def assess_payload(nodes, links, root_key):
    by_key={node['key']:node for node in nodes}
    root=by_key[root_key]
    owned=defaultdict(list);outgoing=defaultdict(list)
    for link in links:
        outgoing[link['source']].append(link)
        if link['field']=='ID' and link.get('target'):
            owned[link['target']].append(link['source'])

    def component(key):
        matches=[l.get('target') for l in outgoing[key] if l['field']=='ComponentID']
        return by_key.get(matches[0]) if len(matches)==1 else None

    placements=[]
    containers={'DataLoadout','DataMount','DataMagazine'}
    if root['table'] in containers:
        placements.append((root_key,root,root['table']))
    for child in owned[root_key]:
        target=component(child)
        expected=target['table'] if target else next((l.get('target_table') for l in outgoing[child] if l['field']=='ComponentID'),None)
        if expected in containers:placements.append((child,target,expected))

    declared=root['fields'].get('WeightPayload') if root['table']=='DataAircraft' else None
    limit=declared if number(declared) and declared>0 else None
    groups=[]
    for placement,container,table in placements:
        sections={'DataLoadout':[('loadout','DataLoadoutWeapons')],
                  'DataMount':[('mount','DataMountWeapons'),('mount_reserve','DataMountMagazineWeapons')],
                  'DataMagazine':[('magazine','DataMagazineWeapons')]}[table]
        for kind,entry_table in sections:
            entries=[by_key[k] for k in owned[container['key']] if by_key[k]['table']==entry_table] if container else []
            if kind=='mount_reserve' and not entries:continue
            items=[]
            for entry in entries:
                record=component(entry['key'])
                if record and record['table']!='DataWeaponRecord':record=None
                weapon=component(record['key']) if record else None
                if weapon and weapon['table']!='DataWeapon':weapon=None
                fields=record['fields'] if record else {}
                quantity,maximum,multiple=(fields.get(f) for f in ('DefaultLoad','MaxLoad','Multiple'))
                weight=weapon['fields'].get('Weight') if weapon else None
                optional=entry['fields'].get('Optional') if kind=='loadout' else 0
                issues=[]
                if record is None:issues.append('weapon_record_unresolved')
                if weapon is None:issues.append('weapon_unresolved')
                valid_quantities=all(number(q) and q>=0 and int(q)==q for q in (quantity,maximum))
                if not valid_quantities:issues.append('quantity_invalid')
                elif quantity>maximum:issues.append('default_exceeds_max')
                if multiple!=1:issues.append('multiple_unresolved')
                if not number(weight) or weight<=0:issues.append('weight_unresolved')
                if optional not in (0,1):issues.append('optional_unresolved')
                mass=quantity*weight if not issues else None
                items.append({'entry_key':entry['key'],'entry_fields':entry['fields'],
                              'weapon_record_key':record['key'] if record else None,
                              'weapon_record_id':record['id'] if record else None,
                              'weapon_key':weapon['key'] if weapon else None,'weapon_id':weapon['id'] if weapon else None,
                              'name':weapon['fields'].get('Name') if weapon else 'Arma sem correspondência',
                              'unit_weight':weight,'default_load':quantity,'max_load':maximum,'multiple':multiple,
                              'optional':None if optional not in (0,1) else bool(optional),
                              'internal':entry['fields'].get('Internal'),
                              'nominal_mass':mass,'issues':issues})
            baseline=[i for i in items if i['optional'] is False]
            complete=container is not None and all(i['optional'] is not None for i in items) and all(i['nominal_mass'] is not None for i in baseline)
            nominal=math.fsum(i['nominal_mass'] for i in baseline) if complete else None
            applicable=kind=='loadout' and bool(items) and limit is not None and nominal is not None
            balance=limit-nominal if applicable else None
            groups.append({'key':placement+':'+kind,'placement_key':placement,
                           'container_key':container['key'] if container else None,'container_table':table,
                           'container_id':container['id'] if container else None,
                           'name':container['fields'].get('Name') if container else 'Componente sem correspondência',
                           'kind':kind,'items':items,'complete_nominal_mass':complete,'nominal_default_mass':nominal,
                           'known_default_subtotal':math.fsum(i['nominal_mass'] for i in baseline if i['nominal_mass'] is not None),
                           'reference_balance':balance,
                           'comparison':'unresolved' if balance is None else 'reference_exceeds' if balance<0 else 'reference_within',
                           'issues':[] if container else ['container_unresolved'],'calculation_ready':False})
    return {'version':VERSION,'root':root_key,'declared_payload':declared,
            'payload_field':'DataAircraft.WeightPayload' if root['table']=='DataAircraft' else None,
            'payload_evidence':root.get('measurements',{}).get('WeightPayload'),
            'weight_evidence':{'unit':None,'candidate_unit':'kg','status':'form_reference','evidence':WEIGHT_SOURCE,
                               'qualification':'Formulário em kg; unidade SQL, unidade de contabilização e massa do sistema completo ainda não comprovadas.'},
            'groups':groups,'operational_available_payload':None,'calculation_ready':False,
            'qualification':'Massas nominais sob hipótese de unidades equivalentes em kg e DefaultLoad como quantidade; não aprovam carregamento. Não incluem automaticamente combustível, tripulação, adaptadores, outras cargas ou limites por ponto. Não somar alternativas.'}
