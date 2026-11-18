import assert from 'node:assert/strict';
import {kinds,classify,silhouette} from './static/unit-silhouettes.mjs';
for(const [name,key] of [['Fragata F-1','frigate'],['Corveta C-1','corvette'],['Contratorpedeiro D-1','destroyer'],['Torpedeiro T-1','torpedo'],['Navio de apoio N-1','support'],['Porta-aviões A-1','carrier'],['Submarino S-1','submarine'],['Aeronave X-1','aircraft'],['Helicóptero H-1','helicopter'],['Meio didático 03','unknown']])assert.equal(classify({name}),key);
assert.equal(classify({category:'Apoio'}),'unknown');
const images=Object.keys(kinds).map(key=>silhouette(key));
assert.equal(new Set(images).size,Object.keys(kinds).length);
for(const key of Object.keys(kinds)){
 const blue=silhouette(key),red=silhouette(key,'#ff7777');
 assert.match(blue,/viewBox="0 0 160 96"/);assert.match(blue,/fill="#4ab6ff"/);assert.match(red,/fill="#ff7777"/);
 assert.equal((blue.match(/<path /g)||[]).length,2);
}
assert.equal(silhouette('constructor'),silhouette('unknown'));
assert.equal(silhouette('__proto__'),silhouette('unknown'));
assert(!silhouette('<script>','" onload="bad').includes('onload'));
console.log('PASS: silhouette families, conservative name/category classification, neutral unknown and static SVG safety');
