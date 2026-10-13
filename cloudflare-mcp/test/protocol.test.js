import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
const endpoint = new URL("https://masalahealth-mcp.neilshahis.workers.dev/mcp");
const fetchWorker = (input, init) => worker.fetch(new Request(input, init));
test("MCP initialization, six annotated tools, resource reads and evaluation", async () => {
  const client = new Client({ name: "verification", version: "1.0.0" });
  await client.connect(
    new StreamableHTTPClientTransport(endpoint, { fetch: fetchWorker }),
  );
  const tools = await client.listTools();
  assert.equal(tools.tools.length, 6);
  assert.ok(tools.tools.every((t) => t.annotations.readOnlyHint));
  const coverage = await client.callTool({
    name: "list_measures",
    arguments: {},
  });
  assert.ok(coverage.structuredContent.count > 0);
  const bmi = await client.callTool({
    name: "evaluate_value",
    arguments: { analyte: "BMI", value: 24, age: 34, unit: "kg/m2" },
  });
  assert.equal(bmi.structuredContent.status, "category");
  const hdl = await client.callTool({
    name: "evaluate_value",
    arguments: { analyte: "HDL", value: 42, unit: "mg/dL" },
  });
  assert.equal(hdl.structuredContent.status, "ambiguous_needs_sex");
  const invalid = await client.callTool({
    name: "evaluate_value",
    arguments: { analyte: "BMI", value: "bad" },
  });
  assert.equal(invalid.isError, true);
  const resource = await client.readResource({ uri: "open-masala://guidance" });
  assert.match(resource.contents[0].text, /provenance_tier/);
  await client.close();
});
test("Health, request paths, CORS and body limits", async () => {
  assert.equal((await fetchWorker("https://example.com/health")).status, 200);
  assert.equal((await fetchWorker("https://example.com/no")).status, 404);
  assert.equal((await fetchWorker(endpoint, { method: "GET" })).status, 405);
  assert.equal(
    (
      await fetchWorker(endpoint, {
        method: "POST",
        headers: { origin: "https://evil.example" },
      })
    ).status,
    403,
  );
  assert.equal(
    (
      await fetchWorker(endpoint, {
        method: "OPTIONS",
        headers: { origin: "https://chatgpt.com" },
      })
    ).status,
    204,
  );
  const huge = await fetchWorker(endpoint, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      accept: "application/json, text/event-stream",
    },
    body: " ".repeat(20000),
  });
  assert.equal(huge.status, 413);
});
