import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js';
import { z } from 'zod';
import * as core from './core.js';
const annotations={readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false};
const analyte=z.string().trim().min(1).max(200),sex=z.enum(['male','female']).optional(),age=z.number().int().min(0).max(130).optional();
export function createServer(){
 const server=new McpServer({name:'masalahealth-open-masala',version:'0.1.0'},{instructions:core.USAGE_RULES+'\n\n'+core.DISCLAIMER+'\nThis server does not retrieve personal app records or store measurements.'});
 const add=(name,description,inputSchema,fn)=>server.registerTool(name,{description,inputSchema,annotations},async args=>{const result=fn(args);return {content:[{type:'text',text:JSON.stringify(result)}],structuredContent:result};});
 add('list_measures','List the analytes and measures covered by Open Masala. Start here for coverage.',{},()=>core.list_measures());
 add('get_reference','Get cited South Asian and general-population references, evidence tiers and overclaim guards. Use an exact returned ID for ambiguous names.',{analyte},a=>core.get_reference(a.analyte));
 add('evaluate_value','Statelessly compare one supplied measurement with a South Asian reference. Always supply the confirmed unit; sex is needed for split references. A reference comparison, not a diagnosis.',{analyte,value:z.number().finite(),sex,age,unit:z.string().trim().min(1).max(50).optional()},a=>core.evaluate_value(a.analyte,a.value,a.sex??null,a.age??null,a.unit??null));
 add('screening_for','Retrieve cited South Asian screening discussion prompts for an age and optional sex. Not a diagnosis or care plan.',{age:z.number().int().min(0).max(130),sex},a=>core.screening_for(a.age,a.sex??null));
 add('search','Search references with lay and clinical terms such as cholesterol, sugar, or kidney.',{query:z.string().trim().min(1).max(200)},a=>core.search(a.query));
 add('list_sources','List unique source citations backing the reference dataset.',{},()=>core.list_sources());
 server.registerResource('dataset','open-masala://dataset',{mimeType:'application/json'},async uri=>({contents:[{uri:uri.href,mimeType:'application/json',text:JSON.stringify(core.DATASET)}]}));
 server.registerResource('guidance','open-masala://guidance',{mimeType:'text/plain'},async uri=>({contents:[{uri:uri.href,mimeType:'text/plain',text:core.USAGE_RULES+'\n\n'+core.DISCLAIMER}]}));
 return server;
}
export default {async fetch(request){
 const url=new URL(request.url);
 if(url.pathname==='/'||url.pathname==='/health')return Response.json({service:'MasalaHealth Open Masala MCP',version:'0.1.0',dataset_version:core.DATASET.version,mcp:'/mcp',scope:'Public reference data; no personal records or persistence.'});
 if(url.pathname!=='/mcp')return new Response('Not found',{status:404});
 const origin=request.headers.get('origin');
 const allowed=new Set(['https://chatgpt.com','https://chat.openai.com','https://platform.openai.com','https://playground.ai.cloudflare.com',url.origin]);
 if(origin&&!allowed.has(origin))return new Response('Origin not allowed',{status:403});
 const headers={'Access-Control-Allow-Origin':origin||'*','Access-Control-Allow-Methods':'POST, GET, OPTIONS','Access-Control-Allow-Headers':'Content-Type, Accept, MCP-Protocol-Version, MCP-Session-Id','Access-Control-Expose-Headers':'MCP-Protocol-Version','Vary':'Origin','Cache-Control':'no-store'};
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers});
 // JSON-only stateless calls do not require a persistent SSE stream.
 if(request.method!=='POST')return new Response('Use MCP Streamable HTTP POST',{status:405,headers:{...headers,Allow:'POST, OPTIONS'}});
 const server=createServer(),transport=new WebStandardStreamableHTTPServerTransport({enableJsonResponse:true,maxRequestBodySize:16384});
 try{await server.connect(transport);const response=await transport.handleRequest(request);const text=await response.text();return new Response(text,{status:response.status,headers:{...Object.fromEntries(response.headers),...headers}});}
 catch{return Response.json({error:'MCP request failed'},{status:500,headers});}
 finally{await server.close();}
}};
