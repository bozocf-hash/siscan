"""Adaptador do par aéreo sintético; resultados transitórios, nunca oficiais."""
from copy import deepcopy
import hashlib
from pathlib import Path
import random

import cpc_judgment as judgment
import cpc_readiness as readiness
import engine_units
import operational_state as state
from cpc_models import Armamento, VetorAereo
from cpc_scenario import CenarioTatico
from cpc_combat import AcaoDisparo, GerenciadorDeCombate
from cpc_time import SimulacaoTemporal

SCHEMA='siscan-cpc-controlled-trial-01'
POLICY='siscan-cpc-controlled-policy-01'
MAX_MINUTES=120


def simular_par(hypotheses,policy,diagnosis):
    """Entradas já diagnosticadas; escolhe somente ações da política declarada.

    shortcut: apenas duas aeronaves sintéticas, ampliar por contrato de grupos.
    Não há seleção otimizada de armas/alvos, perseguição ou navegação geográfica.
    """
    judgment.fields(policy,{'schema_version','initiative','weapons'})
    if policy['schema_version']!=POLICY or policy['initiative'] not in ('simultaneous','AZUL','VERMELHO'):
        raise ValueError('Declare a política e a ordem do ensaio controlado.')
    members=diagnosis['units'];ids={m['unit_id'] for m in members}
    if not isinstance(policy['weapons'],dict) or set(policy['weapons'])!=ids:
        raise ValueError('Declare um estoque ou nenhuma ação para cada meio do par.')
    value=lambda d:d['value']
    scenario={k:value(hypotheses['scenario'][k]) for k in ('duration_minutes','seed','reference','point_scale')}
    if not 1<=scenario['duration_minutes']<=MAX_MINUTES:
        raise ValueError('Este ensaio executa de 1 a 120 minutos; ajuste e confira a duração.')
    entries={u['unit_id']:u for u in hypotheses['units']}
    units=[];positions={};headings={};escape={};chosen={}
    for member in members:
        uid=member['unit_id'];entry=entries[uid];params={k:value(v) for k,v in entry['parameters'].items()}
        if params['estado_voo'] in ('em_voo','evadindo') and params['taxa_consumo_combustivel']<=0:
            raise ValueError('Aeronave em voo exige taxa de consumo positiva para executar.')
        positions[uid]=(params.pop('x'),params.pop('y'));headings[uid]=params.pop('rumo');escape[uid]=params.pop('rumo_evasao');params.pop('availability')
        stocks=[Armamento(identificador=w['estoque_id'],tipo=w['tipo'],**{k:value(w[k]) for k in ('quantidade','pk','dano','alcance_maximo')}) for w in entry['armamentos']]
        unit=VetorAereo(identificador=uid,armamentos=stocks,**params);units.append(unit)
        stock_id=policy['weapons'][uid]
        if stock_id is not None:
            if not isinstance(stock_id,str):raise ValueError('Identidade do estoque inválida.')
            selected=next((w for w in stocks if w.identificador==stock_id),None)
            if selected is None or selected.tipo!='missil_ar_ar':
                raise ValueError('Selecione estoque ar-ar do próprio meio ou nenhuma ação ofensiva.')
            chosen[uid]=selected
    factors={value(f['assinatura_radar']):value(f['fator']) for f in hypotheses['scenario']['fatores_assinatura']}
    pair=tuple(u.identificador for u in units)
    cenario=CenarioTatico(units,{pair:diagnosis['geometry']['distance_nm']},factors,posicoes=positions)
    manager=GerenciadorDeCombate(*units,cenario=cenario,gerador=random.Random(scenario['seed']))
    simulation=SimulacaoTemporal(manager,rumos=headings,rumos_evasao=escape,origem=SCHEMA,semente=scenario['seed'])
    initiative=None if policy['initiative']=='simultaneous' else next(u for u,m in zip(units,members) if m['team']==policy['initiative'])
    reason='duration_completed'
    for minute in range(1,scenario['duration_minutes']+1):
        actions=[AcaoDisparo(f'{minute}:{u.identificador}',u,units[1-i],chosen[u.identificador]) for i,u in enumerate(units) if u.identificador in chosen]
        simulation.avancar_turno(actions,iniciativa=initiative)
        if any(u.pontos_de_vida==0 or u.estado_voo=='perda_proposta' for u in units):
            reason='participant_loss';break
    history=simulation.historico
    return dict(minutes_requested=scenario['duration_minutes'],minutes_completed=simulation.minuto_atual,stop_reason=reason,
                initial=history.estado_inicial,final=history.estado_final,events=history.eventos,balance=history.balanco(),
                metadata={**history.metadados,'policy':deepcopy(policy),'scenario':scenario,
                          'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


def executar_ensaio(db,user,registry,body):
    """Confere fontes antes/depois; só publica o retorno completo em memória."""
    state.autorizar_instrutor(db,user,write=True)
    judgment.fields(body,{'selection','expected_view_sha256','expected_basis_sha256','expected_hypotheses_sha256','hypotheses','policy'})
    if len(engine_units.encoded(body).encode('utf-8'))>64000:raise ValueError('Pedido excede 64 KB.')
    db.execute('SAVEPOINT cpc_controlled_trial_view')
    try:
        diagnosis=readiness.consultar_prontidao(db,user,registry,{k:body[k] for k in ('selection','expected_view_sha256','hypotheses')})
        if diagnosis['basis_sha256']!=body['expected_basis_sha256'] or diagnosis['hypotheses_sha256']!=body['expected_hypotheses_sha256']:
            raise state.Conflict('Base ou hipóteses alteradas; confira as entradas novamente.')
        if not diagnosis['ready_for_controlled_trial']:raise ValueError('Entradas incompletas ou recorte não suportado; confira a prontidão.')
        result=simular_par(body['hypotheses'],body['policy'],diagnosis)
        fresh=judgment.context(db,user,registry,{k:body[k] for k in ('selection','expected_view_sha256')})
        if fresh['basis_sha256']!=diagnosis['basis_sha256']:raise state.Conflict('Base alterada durante o ensaio; resultado descartado.')
        response=dict(schema_version=SCHEMA,exercise_id=diagnosis['exercise_id'],scenario_version=diagnosis['scenario_version'],
                      view_sha256=diagnosis['view_sha256'],basis_sha256=diagnosis['basis_sha256'],hypotheses_sha256=diagnosis['hypotheses_sha256'],
                      policy_sha256=judgment.digest(body['policy']),units=diagnosis['units'],warnings=diagnosis['warnings'],
                      official_effects_applied=False,simulation_started=True,**result)
        engine_units.encoded(response)
        db.execute('RELEASE cpc_controlled_trial_view');return response
    except Exception:
        db.execute('ROLLBACK TO cpc_controlled_trial_view');db.execute('RELEASE cpc_controlled_trial_view');raise
