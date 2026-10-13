# Hosted Open Masala MCP

Cloudflare Workers deployment of the six Open Masala reference tools. Source dataset and evaluation semantics come from `masalahealth/open-masala`, Python MCP version 0.0.3. The dataset is bundled into the Worker; requests do not fetch Hugging Face or invoke a model API.

## Scope

Public reference lookups and stateless evaluation of user-supplied measurements. No personal-record retrieval, database, account authentication, or medication mutations. No application request-body logging. Cloudflare and clients have their own infrastructure/data policies; statelessness is not a promise of zero third-party retention.

Each tool carries read-only, nondestructive, idempotent annotations. Evidence tiers, row-specific citations, overclaim guards, unit mismatches, and unsupported-reference statuses are preserved from the Python implementation. Resource URIs remain `open-masala://dataset` and `open-masala://guidance`.

## Build and verify

```sh
npm ci
npm test
npm run build
npx wrangler deploy --dry-run
```

Tests compare clinical output and metadata against 394 cases generated from the existing Python core (wording of explanations/hints may differ), and exercise MCP initialization, tool discovery, schema rejection, resource reads, CORS, and request-size limits.

`src/dataset.json` must match the Python package's bundled dataset. Refresh the parity fixtures when the canonical data/evaluator changes. The package lock pins deployment dependencies.

## Deploy

The private prototype is live at https://masalahealth-mcp.neilshahis.workers.dev/mcp. See DEPLOYMENT.md for the deployed version and live verification. Current deployment uses restricted Wrangler authorization; GitHub CI verifies changes but does not automatically deploy them.

Connect this repository through Cloudflare Workers Builds. Select the deployment branch, set the root directory to `cloudflare-mcp`, use `npm ci && npm test && npm run build` as the build command, and `npx wrangler deploy` as the deploy command. The configuration creates `masalahealth-mcp` on the existing account's `workers.dev` subdomain and requires no paid bindings.

Alternatively, authenticate Wrangler and run `npm run deploy`. Keep credentials out of Git and plugin packages. Free-plan CPU limits must be verified on the deployed endpoint under representative traffic; successful development tests alone do not prove capacity.

`/health` reports service/dataset versions. `/mcp` supports stateless Streamable HTTP POST and JSON responses; persistent SSE GET streams are not used. Inputs are limited to 16 KiB. Browser origins are limited to ChatGPT, the OpenAI Playground, Cloudflare's playground, and the service's own origin. Server-to-server MCP clients work without an Origin header. Add other browser origins deliberately if needed.

After deployment, verify the real HTTPS endpoint with an MCP client, then rebuild the MasalaHealth plugin with that confirmed URL. Public plugin publication is a separate workflow.

## Attribution

Reference data and original evaluation logic: [Open Masala](https://github.com/masalahealth/open-masala), Masala Health, CC BY 4.0. See LICENSE. The original source citations are retained in every applicable reference result. This dataset is v0, not yet clinician-reviewed; it is not a medical device or a diagnosis/treatment service.
