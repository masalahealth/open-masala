import test from 'node:test';
import assert from 'node:assert/strict';
import fixtures from './python-fixtures.json' with {type:'json'};
import * as core from '../src/core.js';
// Wording and numeric display formatting can differ; clinical values and metadata must match.
function clinical(value){if(Array.isArray(value))return value.map(clinical);if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).filter(([k])=>!['explanation','hint'].includes(k)).map(([k,v])=>[k,clinical(v)]));return value;}
test('Worker results match the Python reference across all fixtures',()=>{for(const f of fixtures)assert.deepEqual(clinical(core[f.tool](...f.args)),clinical(f.expected),`${f.tool} ${JSON.stringify(f.args)}`);});
