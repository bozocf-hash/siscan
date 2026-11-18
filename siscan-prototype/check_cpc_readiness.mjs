import test from 'node:test';
import assert from 'node:assert/strict';
import {createReadinessController} from './static/cpc-readiness.mjs';
const prep={view_sha256:'v',exercise_id:1,scenario_version:1,parties:['AZUL','VERMELHO'].map(team=>({team,group_id:team,composition_revision:1,members:[{unit_id:team}]}))};
const result=()=>({schema_version:'siscan-cpc-trial-readiness-01',view_sha256:'v',exercise_id:1,scenario_version:1,units:[],excluded:[],issues:[],warnings:[],ready_for_controlled_trial:false,official_calculation_ready:false,simulation_started:false,official_effects_applied:false});
function setup(request,options={}){let state;const c=createReadinessController({request,render:s=>state=s,...options});c.setPreparation(prep);return {c,get state(){return state;}};}
test('consulta envia referências e não cria comando de aplicação',async()=>{
 let sent;const e=setup(async(p,o)=>{sent=[p,o.body];return result();});await e.c.check();
 assert.equal(sent[0],'/api/cpc/trial-readiness');assert.equal(sent[1].expected_view_sha256,'v');assert.equal('command_id'in sent[1],false);assert.ok(e.state.result);
});
test('editar e sair descarta resposta atrasada',async()=>{
 let resolve;const e=setup(()=>new Promise(r=>resolve=r));const job=e.c.check();e.c.edit({label:'novo'});resolve(result());await job;
 assert.equal(e.state.result,null);assert.equal(e.state.busy,false);e.c.setPreparation(null);assert.equal(e.state.hypotheses,null);
});
test('cancelar descarte conserva hipótese e consulta',()=>{
 const e=setup(async()=>result(),{confirmDiscard:()=>false});e.c.edit({label:'teste'});assert.equal(e.c.canLeave(),false);assert.equal(e.state.hypotheses.label,'teste');
});
test('401/403 limpam dados privados e comunicam revogação',async()=>{
 for(const status of [401,403]){let forbidden=0;const e=setup(async()=>{throw Object.assign(Error('Negado'),{status});},{onForbidden:()=>forbidden++});await e.c.check();assert.equal(e.state.preparation,null);assert.equal(e.state.result,null);assert.equal(forbidden,1);}
});
test('resposta de outro cenário e falha não viram prontidão',async()=>{
 const e=setup(async()=>({...result(),scenario_version:2}));await e.c.check();assert.equal(e.state.result,null);assert.ok(e.state.error);
 const failed=setup(async()=>{throw Error('Tempo limite de consulta');});await failed.c.check();assert.equal(failed.state.result,null);assert.equal(failed.state.busy,false);assert.ok(failed.state.error);
});

test('campos preservam zero e falso, branco não vira zero e origem exige declaração',async()=>{
 const {hypothesisDatum}=await import('./static/cpc-readiness.mjs');
 assert.equal(hypothesisDatum('',{kind:'number',unit:'kg'},true),undefined);
 assert.deepEqual(hypothesisDatum('0',{kind:'number',unit:'kg'},true),{value:0,unit:'kg',source:'didactic_assumption'});
 assert.equal(hypothesisDatum('false',{kind:'boolean',unit:'1'},true).value,false);
 assert.equal(hypothesisDatum('2',{kind:'number',unit:'kg'},false).source,undefined);
 assert.throws(()=>hypothesisDatum('0.5',{kind:'integer',unit:'item'},true));
});
test('entrada inválida bloqueia envio de perfil anterior',async()=>{
 let calls=0;const e=setup(async()=>{calls++;return result();});e.c.edit({label:'válido'});e.c.inputError('Número inválido');
 assert.equal(await e.c.check(),false);assert.equal(calls,0);assert.equal(e.state.result,null);
});

test('aceitar descarte reinicia os controles mesmo no mesmo par',()=>{
 const e=setup(async()=>result());const version=e.state.formVersion;e.c.edit({label:'descartar'});assert.equal(e.c.canLeave(),true);
 assert.equal(e.state.hypotheses,null);assert.notEqual(e.state.formVersion,version);
});
