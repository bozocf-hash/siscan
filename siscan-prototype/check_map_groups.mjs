import assert from 'node:assert/strict';
import test from 'node:test';
import {createGroupController} from './static/map-groups.mjs';

const data = team => ({team,storage:'memory',warning:'Temporário',exercise_open:true,units:[],groups:[
 {group_id:team,designation:'Grupo',active:true,composition_revision:1,unavailable_count:0,
  members:[{asset_id:team==='AZUL'?1:2,latitude:-22,longitude:-43}]}]});
function fixture(request){
 const frames=[], highlights=[], focuses=[];
 let serial=0;
 const controller=createGroupController({request,render:s=>frames.push(s),highlight:ids=>highlights.push(ids),
  focus:ids=>focuses.push(ids),commandId:()=>`command-${++serial}`});
 return {controller,frames,highlights,focuses};
}
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};

await test('carrega e seleciona sem comando de plotagem',async()=>{
 const calls=[];const f=fixture(async(path,options)=>{calls.push([path,options]);return data('AZUL');});
 await f.controller.load('AZUL');f.controller.select('AZUL');f.controller.focusSelected();
 assert.deepEqual(f.highlights.at(-1),[1]);assert.deepEqual(f.focuses.at(-1),[1]);
 assert.equal(calls.length,1);assert.equal(calls[0][1],undefined);
});
await test('resposta GET atrasada não restaura outro partido',async()=>{
 const blue=deferred();const f=fixture(path=>path.endsWith('AZUL')?blue.promise:Promise.resolve(data('VERMELHO')));
 const loading=f.controller.load('AZUL');await f.controller.load('VERMELHO');f.controller.select('VERMELHO');
 blue.resolve(data('AZUL'));await loading;
 assert.equal(f.frames.at(-1).team,'VERMELHO');assert.deepEqual(f.highlights.at(-1),[2]);
});
await test('erro de leitura não é vazio válido',async()=>{
 const f=fixture(async()=>{throw Error('Sem conexão');});await f.controller.load('AZUL');
 assert.equal(f.frames.at(-1).data,null);assert.equal(f.frames.at(-1).error,'Sem conexão');
});
await test('reenvio usa mesmo comando e intenção editada usa outro',async()=>{
 const payloads=[];const f=fixture(async(path,options)=>{
  if(!options)return data('AZUL');payloads.push(options.body);throw Error('Sem resposta');
 });
 await f.controller.load('AZUL');const input={designation:'Teste',domain:'aereo',member_unit_ids:['u2','u1']};
 await f.controller.create(input);await f.controller.create({...input,member_unit_ids:['u1','u2']});
 assert.equal(payloads[0].command_id,payloads[1].command_id);
 await f.controller.create({...input,designation:'Editado'});
 assert.notEqual(payloads[1].command_id,payloads[2].command_id);
 assert.deepEqual(Object.keys(payloads[0]).sort(),['command_id','designation','domain','member_unit_ids','team']);
});
await test('POST atrasado não abre seleção de outro contexto',async()=>{
 const post=deferred();const f=fixture((path,options)=>options?post.promise:Promise.resolve(data(path.endsWith('AZUL')?'AZUL':'VERMELHO')));
 await f.controller.load('AZUL');const writing=f.controller.create({designation:'Teste',domain:'aereo',member_unit_ids:['u']});
 await f.controller.load('VERMELHO');post.resolve({group:{group_id:'AZUL'}});await writing;
 assert.equal(f.frames.at(-1).team,'VERMELHO');assert.equal(f.frames.at(-1).selectedGroup,null);
 assert.deepEqual(f.highlights.at(-1),[]);
});
await test('arquivar inclui revisão esperada e recarrega lista',async()=>{
 let posted;const f=fixture(async(path,options)=>{if(options){posted=[path,options.body];return {group:{group_id:'AZUL'}};}return data('AZUL');});
 await f.controller.load('AZUL');await f.controller.archive('AZUL');
 assert.equal(posted[0],'/api/map-unit-groups/AZUL/archive');assert.equal(posted[1].expected_revision,1);
});
await test('vínculos ausentes não viram marcadores',async()=>{
 const d=data('AZUL');d.groups[0].members=[];d.groups[0].unavailable_count=1;
 const f=fixture(async()=>d);await f.controller.load('AZUL');f.controller.select('AZUL');f.controller.focusSelected();
 assert.deepEqual(f.highlights.at(-1),[]);assert.deepEqual(f.focuses.at(-1),[]);
});
await test('exercício encerrado impede comandos na interface',async()=>{
 let writes=0;const d=data('AZUL');d.exercise_open=false;
 const f=fixture(async(path,options)=>{if(options)writes++;return d;});
 await f.controller.load('AZUL');await f.controller.create({designation:'Teste',domain:'aereo',member_unit_ids:['u']});
 await f.controller.archive('AZUL');assert.equal(writes,0);
});
await test('consulta individual realça apenas vínculo visível e não grava',async()=>{
 const f=fixture(async()=>data('AZUL'));await f.controller.load('AZUL');f.controller.select('AZUL');
 f.controller.inspectMember(1);assert.deepEqual(f.highlights.at(-1),[1]);
 f.controller.inspectMember(999);assert.deepEqual(f.highlights.at(-1),[]);
});
