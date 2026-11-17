import test from 'node:test';
import assert from 'node:assert/strict';
import {calungaForParty,judgmentStage} from './static/map-presentation.mjs';
test('Calunga preserva o SVG hostil e o amigo entregues pelo motor',()=>{
 const generated={symbol_svg:'<svg>amigo</svg>',hostile_symbol_svg:'<svg>hostil</svg>'};
 assert.equal(calungaForParty(generated,'AZUL'),generated.symbol_svg);
 assert.equal(calungaForParty(generated,'VERMELHO'),generated.hostile_symbol_svg);
});
test('julgamento revela somente a etapa correspondente ao estado',()=>{
 assert.equal(judgmentStage({}),'start');
 assert.equal(judgmentStage({basis:{}}),'edit');
 assert.equal(judgmentStage({basis:{},preview:{},dirty:true}),'preview');
 assert.equal(judgmentStage({basis:{},preview:{},proposal:{},dirty:false}),'saved');
 assert.equal(judgmentStage({proposal:{},dirty:false}),'unavailable');
 assert.equal(judgmentStage({preview:{},proposal:{},confirming:true}),'confirm');
 assert.equal(judgmentStage({receipt:{},confirming:true}),'result');
 assert.equal(judgmentStage({basis:{},proposal:{},dirty:true}),'edit');
});
