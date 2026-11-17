import assert from 'node:assert/strict';
import test from 'node:test';
import {createCpcController} from './static/cpc-preparation.mjs';
const list=()=>({exercise_id:1,scenario_version:1,exercise_open:true,storage:'memory',parties:['AZUL','VERMELHO'].map(team=>({team,groups:[{group_id:team,designation:team,composition_revision:2,preparable:true}]}))});
const pair=()=>({exercise_id:1,scenario_version:1,schema_version:'siscan-cpc-map-preparation-01',parties:['AZUL','VERMELHO'].map(team=>({team,group_id:team,composition_revision:2,members:[]})),simulation_started:false,official_calculation_ready:false,official_effects_applied:false});
const defer=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {resolve,reject,promise};};
function fixture(request){const frames=[],previews=[];const controller=createCpcController({request,render:s=>frames.push(s),preview:p=>previews.push(p)});return {controller,frames,previews};}
const choose=c=>{c.choose('AZUL','AZUL');c.choose('VERMELHO','VERMELHO');};

await test('retomada restaura somente par disponível do contexto atual',async()=>{
 const f=fixture(async()=>list());await f.controller.enter();assert.equal(f.controller.restore(pair()),true);
 assert.equal(f.frames.at(-1).selection.AZUL,'AZUL');assert.equal(f.previews.at(-1).parties.length,2);
 assert.equal(f.controller.restore({...pair(),scenario_version:2}),false);
 const stale=pair();stale.parties[0].composition_revision=1;assert.equal(f.controller.restore(stale),false);
});

await test('seleção explícita prepara revisões, sem campos de efeitos',async()=>{
 let posted;const f=fixture(async(path,options)=>{if(options){posted=options.body;return pair();}return list();});
 await f.controller.enter();assert.equal(f.frames.at(-1).selection.AZUL,null);choose(f.controller);await f.controller.prepare();
 assert.deepEqual(posted,{AZUL:{group_id:'AZUL',expected_revision:2},VERMELHO:{group_id:'VERMELHO',expected_revision:2}});
 assert.equal(f.previews.at(-1).simulation_started,false);
});
await test('grupo indisponível ou desconhecido não é enviado',async()=>{
 let writes=0;const d=list();d.parties[0].groups[0].preparable=false;
 const f=fixture(async(path,o)=>{if(o)writes++;return d;});await f.controller.enter();choose(f.controller);await f.controller.prepare();
 assert.equal(writes,0);assert.equal(f.frames.at(-1).selection.AZUL,null);
});
await test('mudança de seleção invalida par e descarta POST antigo',async()=>{
 const post=defer();const f=fixture(async(path,o)=>o?post.promise:list());await f.controller.enter();choose(f.controller);
 const writing=f.controller.prepare();f.controller.choose('AZUL',null);post.resolve(pair());await writing;
 assert.equal(f.frames.at(-1).preparation,null);assert.equal(f.previews.at(-1),null);
});
await test('sair durante carga não restaura listas ou camada',async()=>{
 const read=defer();const f=fixture(()=>read.promise);const loading=f.controller.enter();f.controller.leave();read.resolve(list());await loading;
 assert.equal(f.frames.at(-1).active,false);assert.equal(f.frames.at(-1).list,null);assert.equal(f.previews.at(-1),null);
});
await test('sair durante POST descarta conferência',async()=>{
 const post=defer();const f=fixture(async(path,o)=>o?post.promise:list());await f.controller.enter();choose(f.controller);
 const writing=f.controller.prepare();f.controller.leave();post.resolve(pair());await writing;
 assert.equal(f.frames.at(-1).active,false);assert.equal(f.previews.at(-1),null);
});
await test('contexto divergente exige atualizar fontes',async()=>{
 const f=fixture(async(path,o)=>o?{...pair(),scenario_version:2}:list());await f.controller.enter();choose(f.controller);await f.controller.prepare();
 assert.equal(f.frames.at(-1).list,null);assert.match(f.frames.at(-1).error,/contexto|cenário/i);assert.equal(f.previews.at(-1),null);
});
await test('403 limpa dados dos dois partidos',async()=>{
 const f=fixture(async(path,o)=>{if(o)throw Object.assign(Error('Negado'),{status:403});return list();});
 await f.controller.enter();choose(f.controller);await f.controller.prepare();assert.equal(f.frames.at(-1).list,null);assert.equal(f.previews.at(-1),null);
});
await test('exercício encerrado não prepara; erro não é lista vazia',async()=>{
 let writes=0;const d=list();d.exercise_open=false;
 const f=fixture(async(path,o)=>{if(o)writes++;return d;});await f.controller.enter();choose(f.controller);await f.controller.prepare();assert.equal(writes,0);
 const failed=fixture(async()=>{throw Error('Sem conexão');});await failed.controller.enter();assert.equal(failed.frames.at(-1).list,null);assert.equal(failed.frames.at(-1).error,'Sem conexão');
});
await test('resposta não pode substituir o grupo escolhido',async()=>{
 const bad=pair();bad.parties[0].group_id='OUTRO';const f=fixture(async(path,o)=>o?bad:list());
 await f.controller.enter();choose(f.controller);await f.controller.prepare();assert.equal(f.frames.at(-1).preparation,null);assert.equal(f.previews.at(-1),null);
});
