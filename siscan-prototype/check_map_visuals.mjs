import assert from 'node:assert/strict';
import {kinds,classify,silhouette} from './static/unit-silhouettes.mjs';
for(const [name,key] of [['Fragata F-1','frigate'],['Corveta C-1','corvette'],['Contratorpedeiro D-1','destroyer'],['Torpedeiro T-1','torpedo'],['Navio de apoio N-1','support'],['Porta-aviões A-1','carrier'],['Submarino S-1','submarine'],['Aeronave X-1','aircraft'],['Helicóptero H-1','helicopter'],['Meio didático 03','unknown']])assert.equal(classify({name}),key);
assert.equal(classify({category:'Apoio'}),'unknown');
for(const key of Object.keys(kinds))assert.match(silhouette(key),/^<svg/);
assert(!silhouette('<script>','" onload="bad').includes('onload'));
console.log('PASS: silhouette families, conservative name/category classification, neutral unknown and static SVG safety');
