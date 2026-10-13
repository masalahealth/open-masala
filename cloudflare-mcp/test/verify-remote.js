import assert from 'node:assert/strict';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
const endpoint=new URL(process.argv[2]);
const health=await fetch(new URL('/health',endpoint));assert.equal(health.status,200);console.log('Health',await health.json());
const client=new Client({name:'masalahealth-deployment-verification',version:'0.1.0'});
try{
 await client.connect(new StreamableHTTPClientTransport(endpoint));
 const tools=await client.listTools();assert.equal(tools.tools.length,6);assert.ok(tools.tools.every(t=>t.annotations.readOnlyHint));console.log('Six read-only tools discovered');
 const resource=await client.readResource({uri:'open-masala://guidance'});assert.match(resource.contents[0].text,/provenance_tier/);console.log('Guidance resource read');
 const cases=[['list_measures',{},r=>r.count>0],['get_reference',{analyte:'BMI'},r=>r.matches.length>0],['evaluate_value',{analyte:'BMI',value:24,age:34,unit:'kg/m2'},r=>r.status==='category'],['evaluate_value',{analyte:'HDL',value:42,unit:'mg/dL'},r=>r.status==='ambiguous_needs_sex'],['evaluate_value',{analyte:'ApoB',value:1.1,unit:'g/L'},r=>r.status==='unit_mismatch'],['evaluate_value',{analyte:'eGFR',value:90},r=>r.status==='do_not_apply'],['screening_for',{age:34},r=>Array.isArray(r.applicable)],['search',{query:'cholesterol'},r=>r.count>0],['list_sources',{},r=>r.count>0]];
 for(const [name,args,check] of cases){const result=await client.callTool({name,arguments:args});assert.ok(!result.isError,`${name}: ${JSON.stringify(result)}`);assert.ok(check(result.structuredContent),name);console.log(name,'PASS');}
 console.log('LIVE ENDPOINT VERIFICATION PASSED');
}finally{await client.close();}
