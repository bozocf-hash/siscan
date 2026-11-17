import test from 'node:test';
import assert from 'node:assert/strict';
import {createJudgmentController} from './static/cpc-judgment.mjs';
const preparation={view_sha256:'view',parties:['AZUL','VERMELHO'].map(team=>({team,group_id:team,composition_revision:1,members:[]}))};
const basis={basis_sha256:'basis',selection:{},preparation,states:{u:{state:{revision:0,index_percent:null,lost:null}}}};
function setup(request,options={}){let state;const calls=[];const c=createJudgmentController({request:async(...args)=>{calls.push(args);return request(...args);},render:s=>state=s,onOfficial:()=>{},confirmDiscard:()=>false,...options});c.setPreparation(preparation);return {c,calls,get state(){return state;}};}
const draft={enabled:true,indexAction:'set',indexValue:'60',lossAction:'keep'};
test('prévia não aplica e vazio não vira zero',async()=>{
 const env=setup(async(path)=>path.endsWith('/context')?basis:{basis,effects:[]});await env.c.open();env.c.reason('Aula');
 env.c.edit('u',{...draft,indexValue:''});assert.equal(await env.c.preview(),false);assert.equal(env.calls.length,1);
 env.c.edit('u',draft);await env.c.preview();assert.equal(env.calls.at(-1)[1].body.effects[0].changes.index_percent,60);
 assert.ok(env.calls.every(([p])=>!p.endsWith('/decisions')));
});
test('confirmação requer proposta salva e ação final separada',async()=>{
 const env=setup(async path=>path.endsWith('/context')?basis:path.endsWith('/preview')?{basis,effects:[]}:path.endsWith('/decisions')?{decision_id:'d',action:'confirm'}:{proposal_id:'p',revision:1,body_sha256:'sha'});
 await env.c.open();env.c.reason('Aula');env.c.edit('u',draft);await env.c.preview();assert.equal(await env.c.decide('confirm'),false);
 await env.c.save();assert.equal(await env.c.decide('confirm'),false);env.c.review();await env.c.decide('confirm');
 assert.equal(env.state.receipt.decision_id,'d');assert.equal(env.calls.filter(([p])=>p.endsWith('/decisions')).length,1);
});
test('resposta perdida mantém UUID e mesma intenção no retry',async()=>{
 let failed=false;const env=setup(async path=>{if(path.endsWith('/context'))return basis;if(path.endsWith('/preview'))return {basis,effects:[]};if(!failed){failed=true;throw Error('rede');}return {proposal_id:'p',revision:1,body_sha256:'s'};});
 await env.c.open();env.c.reason('Aula');env.c.edit('u',draft);await env.c.preview();await env.c.save();
 const body=env.calls.at(-1)[1].body;assert.ok(env.state.pending);await env.c.retry();assert.deepEqual(env.calls.at(-1)[1].body,body);
});
test('trocar contexto descarta resposta antiga',async()=>{
 let resolve;const env=setup(()=>new Promise(r=>resolve=r));const job=env.c.open();env.c.setPreparation(null);resolve(basis);await job;
 assert.equal(env.state.basis,null);
});
test('edição não salva impede saída sem aceite',async()=>{
 const env=setup(async()=>basis);await env.c.open();env.c.reason('rascunho');assert.equal(env.c.canLeave(),false);
});
test('aceitar descarte limpa a edição e a proposta da vista antes do histórico',async()=>{
 const env=setup(async path=>path.endsWith('/context')?basis:path.endsWith('/preview')?{basis,effects:[]}:path.includes('?')?{items:[],next_cursor:null}:{proposal_id:'p',revision:1,body_sha256:'sha'}, {confirmDiscard:()=>true});
 await env.c.open();env.c.reason('Aula');env.c.edit('u',draft);await env.c.preview();await env.c.save();
 env.c.edit('u',{indexValue:'30'});await env.c.history();assert.equal(env.state.basis,null);assert.equal(env.state.proposal,null);
 assert.equal(env.c.review(),false);assert.equal(await env.c.decide('confirm'),false);
});
test('refresh falho após commit mantém recibo oficial',async()=>{
 let contexts=0;const env=setup(async path=>{if(path.endsWith('/context')){if(++contexts>1)throw Error('refresh');return basis;}if(path.endsWith('/preview'))return {basis,effects:[]};if(path.endsWith('/decisions'))return {decision_id:'d',action:'confirm'};return {proposal_id:'p',revision:1,body_sha256:'s'};});
 await env.c.open();env.c.reason('Aula');env.c.edit('u',draft);await env.c.preview();await env.c.save();env.c.review();await env.c.decide('confirm');
 assert.equal(env.state.receipt.action,'confirm');assert.equal(env.state.refreshPending,true);assert.equal(env.state.pending,null);
});
test('403 limpa base, proposta e histórico',async()=>{
 const env=setup(async path=>{if(path.endsWith('/context'))return basis;throw Object.assign(Error('revogado'),{status:403});});
 await env.c.open();await env.c.history();assert.equal(env.state.basis,null);assert.deepEqual(env.state.history,[]);
});
test('retomada com grupo ausente impede confirmar',async()=>{
 const view={proposal_id:'p',available:false,availability_reason:'Grupo ausente',correction_decision_id:null,decision:null,receipt:null,
  current:{revision:1,body_sha256:'sha',body:{origin:{basis},reason:'Aula',effects:[{refs:{unit_id:'u'},changes:{index_percent:60}}]}}};
 const env=setup(async()=>view);await env.c.resume('p');assert.equal(env.state.notice,'Grupo ausente');
 assert.equal(env.c.review(),false);assert.equal(await env.c.decide('confirm'),false);
});
test('retomada disponível restaura explicitamente o par conferido',async()=>{
 let restored;const view={available:true,decision:null,receipt:null,correction_decision_id:null,
  current:{revision:1,body_sha256:'s',body:{origin:{basis},reason:'Aula',effects:[{refs:{unit_id:'u'},changes:{index_percent:60}}]}}};
 const env=setup(async path=>path.endsWith('/preview')?{basis,effects:[]}:view,{onResumePair:p=>{restored=p;return true;}});
 await env.c.resume('p');assert.deepEqual(restored,preparation);assert.equal(env.state.dirty,false);assert.equal(env.c.review(),true);
});
test('refresh atrasado não restaura contexto abandonado',async()=>{
 let contexts=0,resolve;const env=setup(async path=>{if(path.endsWith('/context'))return ++contexts===1?basis:new Promise(r=>resolve=r);
  if(path.endsWith('/preview'))return {basis,effects:[]};if(path.endsWith('/decisions'))return {decision_id:'d',action:'confirm'};return {proposal_id:'p',revision:1,body_sha256:'sha'};});
 await env.c.open();env.c.reason('Aula');env.c.edit('u',draft);await env.c.preview();await env.c.save();env.c.review();
 const job=env.c.decide('confirm');while(!resolve)await Promise.resolve();env.c.setPreparation(null);resolve(basis);await job;assert.equal(env.state.basis,null);
});

test('decisão atualiza o status do registro já exibido no histórico',async()=>{
 const env=setup(async path=>path.includes('?')?{items:[{proposal_id:'p',status:'pending'}],next_cursor:null}:path.endsWith('/context')?basis:path.endsWith('/preview')?{basis,effects:[]}:path.endsWith('/decisions')?{decision_id:'d',action:'confirm'}:{proposal_id:'p',revision:1,body_sha256:'sha'});
 await env.c.open();env.c.reason('Aula');env.c.edit('u',draft);await env.c.preview();await env.c.save();await env.c.history();
 assert.equal(env.state.history[0].status,'pending');env.c.review();await env.c.decide('confirm');
 assert.equal(env.state.history[0].status,'confirm');assert.equal(env.state.receipt.action,'confirm');
});
